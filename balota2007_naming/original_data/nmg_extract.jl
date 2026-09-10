using Arrow, CategoricalArrays, CSV, DataFrames, Dates, PooledArrays, ZipFile

include("utils.jl")

const SKIPLIST = String[  # list of redundant or questionable files
    "Data2815.NMG",
    "Data2816.NMG",
    "Data2817.NMG",
    "Data2818.NMG",
    "Data2819.NMG",
    "Data2820.NMG",
    "Data2821.NMG",
    "Data2778.NMG",
    "Data2779.NMG",
    "Data4140.NMG",
    "Data4100.NMG",
    "Data4140.NMG",
    "Data4110.NMG",
    "Data4140.NMG",
    "283DATA.NMG",
    "Data3872.NMG",
    "Data3882.NMG",
    "Data3884.NMG",
    "Data3886.NMG",
    "Data3894.NMG",
    "371DATA.NMG",
    "Data3911.NMG",
    "Data3912.NMG",
    "Data3930.NMG",
    "Data4210.NMG",
    "Data4118.NMG",
    "Data4119.NMG",
    "Data5255.NMG",
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
                header=[:seq, :itemno, :codrt, :code, :nmgrt, :item],
                comment="=",
                types=[Int16, Int32, Int16, Int8, Int16, String],
            )
        )
    )
end

"""
    parse_nmg_file(f::ZipFile.ReadableFile)

Return a NamedTuple of `f.name` and 6 DataFrames from NMG file in the zip archive
"""
function parse_nmg_file(f::ZipFile.ReadableFile)
    @show f.name
    global univ, sess1, sess2, subj, ncor, hlth
    hdrbuf, trialbuf = IOBuffer(), IOBuffer()        # in-memory "files"
    univhdr = "Univ,Time,Date,Subject,Age,Education" # occurs in line 1 and after seq 2000
    subjhdr = "Subject,Gender,Task,MEQ,Time,Date"    # marks demog block at file end
    ncorhdr = "numCorrect,rawScore,vocabAge,shipTime,readTime"
    hlthhdr = "presHealth,pastHealth,vision,hearing,firstLang"
    keep = true                                      # pass as named argument to readline
    fnm = f.name
    ln = readline(f; keep)
    if !startswith(ln, univhdr)
        throw(ArgumentError("$(f.name) does not start with expected header"))
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

dfs = open("./nmg_raw.zip", "r") do io
    [parse_nmg_file(f)  for f in filter(f -> f.name ∉ SKIPLIST, ZipFile.Reader(io).files)];
end

"""
    getDOB(nt::NamedTuple)

Return the last value of `asDate.(nt.univ.DOB, Ref(nt.fnm))`
"""
getDOB(nt) = last(asDate.(nt.univ.Age, Ref(nt.fnm)))

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
    [:subj, :univ],
)

subjtbl.sex = PooledArray(subjtbl.sex; compress=true, signed=true);
subjtbl.frstLang = PooledArray(subjtbl.frstLang; compress=true, signed=true);
subjtbl.univ = let
    levs = ["Morehead","SUNY-Albany","Kansas","South Florida","Wash. Univ","Wayne State"]
    CategoricalArray(levs[subjtbl.univ]; levels=levs)
end;
subjtbl.rawscor = [(ismissing(x) || x < 3) ? missing : x for x in subjtbl.rawscor];
subjtbl.ncorrct = [(ismissing(x) || x < 3) ? missing : x for x in subjtbl.ncorrct];
subjtbl.vocabAge = [(ismissing(x) || x < 3 || x > 25) ? missing : x for x in subjtbl.vocabAge];
subjtbl.readTime = [(ismissing(x) || x < 0) ? missing : x for x in subjtbl.readTime];
subjtbl.MEQ = [(ismissing(x) || x < 3) ? missing : x for x in subjtbl.MEQ];
Arrow.write("./arrow/nmg_subj.arrow", subjtbl; compress=:zstd)

"""
    trtbl(nt)

Return a `DataFrame` of the trial information from a `NamedTuple`, including `subj` column.
"""
function trtbl(nt)
    subj, sess1, sess2 = checksubj(nt), nt.sess1, nt.sess2
    if (any(sess1.seq .> 1500) || any(sess2.seq .< 1501))
        throw(ArgumentError("sequence and session are inconsistent in $(nt.fnm)"))
    end
    return select(
        append!(copy(sess1), sess2),
        1 => (x -> subj) => :subj,
        :seq,
        :itemno,
        :codrt,
        :code,
        :nmgrt,
        :item
        )
end 
    
trials = sort(foldl(append!, [trtbl(nt) for nt in dfs]), [:subj, :seq])
itemtbl = sort!(unique(select(trials, :itemno, :item)), :itemno)
trials.item = CategoricalArray(trials.item; levels = itemtbl.item, ordered=true)
Arrow.write("./arrow/nmg_trial.arrow", select(trials, Not(:itemno)); compress=:zstd)

# Incorporate information from Items.csv

asInt(v) = passmissing(parse).(Int, passmissing(replace).(v, ',' => ""))
asFloat(v) = passmissing(parse).(Float32, passmissing(replace).(v, ',' => ""))
items = select!(
    DataFrame(CSV.File("./Items.csv.gz"; missingstring="#")),
    :,
    :Freq_KF => asInt,
    :Freq_HAL => asInt,
    :SUBTLWF => asFloat,
    :Semantic_Neighbors => asInt,
    :Assoc_Freq_R1 => asInt,
    :Assoc_Types_R1 => asInt,
    :Assoc_Freq_R123 => asInt,
    :Assoc_Types_R123 => asInt,
    :BG_Sum => asInt,
    :BG_Mean => asFloat,
    :BG_Freq_By_Pos => asInt,
    :I_Mean_RT => asFloat,
    :I_NMG_Mean_RT => asFloat;
    renamecols = false,
)
            # reduce sizes of stored values
asInt8(v) = passmissing(Int8).(v)
asInt16(v) = passmissing(Int16).(v)
asInt32(v) = passmissing(Int32).(v)
asFloat32(v) = passmissing(Float32).(v)

for nm in names(items, Union{Missing,Float64})
    items[!, nm] = asFloat32(items[!, nm])
end

select!(items,
    :,
    :Length => asInt8,
    :Freq_KF => asInt32,
    :Freq_HAL => asInt32,
    :Ortho_N => asInt8,
    :Phono_N => asInt8,
    :Phono_N_H => asInt8,
    :OG_N => asInt8,
    :OG_N_H => asInt8,
    :Freq_Greater => asInt8,
    :Freq_Less => asInt8,
    :Semantic_Neighbors => asInt16,
    :Assoc_Freq_R1 => asInt16,
    :Assoc_Types_R1 => asInt16,
    :Assoc_Freq_R123 => asInt16,
    :Assoc_Types_R123 => asInt16,
    :BG_Sum => asInt32,
    :BG_Freq_By_Pos => asInt16,
    :NPhon => asInt8,
    :NSyll => asInt8,
    :NMorph => asInt8,
    :Obs => asInt8,
    :I_NMG_Obs => asInt8;
    renamecols = false,
)

Arrow.write("./arrow/nmg_item.arrow",
    disallowmissing!(
        leftjoin(
            itemtbl,
            rename!(items, :Word => :item);
            on=:item,
        );
        error=false,
    );
    compress=:zstd,
)
