using Arrow
using CategoricalArrays
using CSV
using DataFrames
using Dates
using PooledArrays
using ZipFile

include("utils.jl")

const SKIPLIST = [  # list of redundant or questionable files
    "9999.LDT",
    "793DATA.LDT",
    "Data999.LDT",
    "Data1000.LDT",
    "Data1010.LDT",
    "Data1016.LDT",
];

"""
    checktbuf!(buf::IOBuffer)

Return a DataFrame of the contents of `buf` assuming it contains trial information
"""
function checktbuf!(buf)
    return(
        DataFrame(
            CSV.File(
                take!(buf);          # extract contents of and empty buf
                header=[:seq, :itemgrp, :wrd, :acc, :rt, :item],
                comment="=",
                types=[Int16, Int32, Bool, Int8, Int16, String],
            )
        )
    )
end

"""
    parse_ldt_file(f::ZipFile.ReadableFile)

Return a NamedTuple of `fnm` and 6 DataFrames from LDT file in the zip archive
"""
function parse_ldt_file(f::ZipFile.ReadableFile)
    @show f.name
    global univ, sess1, sess2, subj, ncor, hlth
    hdrbuf, trialbuf = IOBuffer(), IOBuffer()        # in-memory "files"
    univhdr = "Univ,Time,Date,Subject,DOB,Education" # occurs in line 1 and after seq 2000
    subjhdr = "Subject,Gender,Task,MEQ,Time,Date"    # marks demog block at file end
    ncorhdr = "numCorrect,rawScore,vocabAge,shipTime,readTime"
    hlthhdr = "presHealth,pastHealth,vision,hearing,firstLang"
    keep = true                                      # pass as named argument to readline
    fnm = f.name
    ln = readline(f; keep)
    if !startswith(ln, univhdr)
        throw(ArgumentError("$fnm does not start with expected header"))
    end
    write(hdrbuf, ln)
    write(hdrbuf, readline(f; keep))
    ln = readline(f; keep)
    while true     # loop over lines in file
        if startswith(ln, univhdr)   # header for session 2
            write(hdrbuf, readline(f; keep))   # second line of univ data
            univ = checkhbuf!(hdrbuf, [Int8, String, String, Int16, String, Int8])
            sess1 = checktbuf!(trialbuf)
        elseif startswith(ln, subjhdr)
            sess2 = checktbuf!(trialbuf)
            write(hdrbuf, ln)
            write(hdrbuf, readline(f; keep))
            subj = checkhbuf!(
                hdrbuf,
                [Int16, String, String, Float32, String, String],
                ["","00:00:00","00-00-0000", "x"],
            )
            ln = skipblanks(f)
            startswith(ln, ncorhdr) || throw(ArgumentError("Expected $ncorhdr, got $ln"))
            write(hdrbuf, ln)
            write(hdrbuf, readline(f; keep))
            ncor = checkhbuf!(hdrbuf, [Int8, Int8, Float32, Int8, Float32], "999")
            ln = skipblanks(f)
            startswith(ln, hlthhdr) || throw(ArgumentError("Expected $hlthhdr, got $ln"))
            write(hdrbuf, ln)
            write(hdrbuf, readline(f; keep))
            hlth = checkhbuf!(hdrbuf, [Int8, Int8, Int8, Int8, String], ["","Unknown","-1"])
            break
        else
            write(trialbuf, ln)
        end
        ln = readline(f; keep)
    end
    return (; fnm, univ, sess1, sess2, subj, ncor, hlth)
end

dfs = open("./ldt_raw.zip", "r") do io
    [parse_ldt_file(f)  for f in filter(f -> f.name ∉ SKIPLIST, ZipFile.Reader(io).files)];
end

"""
    getDOB(nt::NamedTuple)

Return the last value of `asDate.(nt.univ.DOB, Ref(nt.fnm))`
"""
getDOB(nt) = last(asDate.(nt.univ.DOB, Ref(nt.fnm)))

subjtbl = sort!(
    DataFrame(
        [
            (
                subj = checksubj(nt),
                univ = only(unique(nt.univ.Univ)),
                sex = only(nt.subj.Gender),
                DOB = getDOB(nt),
                MEQ = only(nt.subj.MEQ),
                vision = only(nt.hlth.vision),
                hearing = only(nt.hlth.hearing),
                educatn = getEduc(nt),
                ncorrct = only(nt.ncor.numCorrect),
                rawscor = only(nt.ncor.rawScore),
                vocabAge = only(nt.ncor.vocabAge),
                shipTime = only(nt.ncor.shipTime),
                readTime = only(nt.ncor.readTime),
                preshlth = only(nt.hlth.presHealth),
                pasthlth = only(nt.hlth.pastHealth),
                S1start = parseDateTime(first(nt.univ)),
                S2start = parseDateTime(last(nt.univ)),
                MEQstrt = parseDateTime(only(nt.subj)),
                filename = nt.fnm,
                frstLang = only(nt.hlth.firstLang),
            ) for nt in dfs
        ]
    ),
    :subj
)

subjtbl.sex = PooledArray(subjtbl.sex; compress=true, signed=true);
subjtbl.frstLang = PooledArray(subjtbl.frstLang; compress=true, signed=true);
subjtbl.rawscor = [(ismissing(x) || x < 3) ? missing : x for x in subjtbl.rawscor];
subjtbl.ncorrct = [(ismissing(x) || x < 3) ? missing : x for x in subjtbl.ncorrct];
subjtbl.vocabAge = [(ismissing(x) || x < 3 || x > 25) ? missing : x for x in subjtbl.vocabAge];
subjtbl.readTime = [(ismissing(x) || x < 0) ? missing : x for x in subjtbl.readTime];
subjtbl.MEQ = [(ismissing(x) || x < 3) ? missing : x for x in subjtbl.MEQ];
subjtbl.univ = let
    levs = ["Morehead","SUNY-Albany","Kansas","South Florida","Wash. Univ","Wayne State"]
    CategoricalArray(levs[subjtbl.univ]; levels=levs)
end

Arrow.write("./arrow/ldt_subj.arrow", disallowmissing!(subjtbl; error=false); compress=:zstd)

"""
    trtbl(nt)

Return a `DataFrame` of the trial information from a `NamedTuple`, including `subj` column.
"""
function trtbl(nt)
    subj, sess1, sess2 = checksubj(nt), nt.sess1, nt.sess2
    if (any(sess1.seq .> 2000) || any(sess2.seq .< 2001))
        throw(ArgumentError("sequence and session are inconsistent in $(nt.fnm)"))
    end
    return select(
        append!(copy(sess1), sess2),
        1 => (x -> subj) => :subj,
        :seq,
        [:itemgrp, :wrd] => ((x,y) -> Int32.(2 * x - y)) => :itemno,
        :acc,
        :rt,
        :item
        )
end 
    
trials = sort(foldl(append!, [trtbl(nt) for nt in dfs]), [:subj, :seq])
trials.acc = BoolOrMsng.(trials.acc)
itemtbl = sort!(unique(select(trials, :itemno, :item)), :itemno)
trials.item = CategoricalArray(trials.item; levels = itemtbl.item, ordered=true)
Arrow.write("./arrow/ldt_trial.arrow", select(trials, Not(:itemno)); compress=:zstd)

if "isword" ∉ names(itemtbl)
    itemtbl.isword = isodd.(itemtbl.itemno)
end
if "wrdlen" ∉ names(itemtbl)
    itemtbl.wrdlen = Int8.(length.(itemtbl.item))
end
if "pairno" ∉ names(itemtbl)
    itemtbl.pairno = Int32.((itemtbl.itemno + itemtbl.isword) .>> 1)
end
Arrow.write("./arrow/ldt_item.arrow", itemtbl; compress=:zstd)
