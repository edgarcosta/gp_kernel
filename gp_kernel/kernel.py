from ipykernel.kernelbase import Kernel
from pexpect import EOF, TIMEOUT, spawn
from tempfile import NamedTemporaryFile

from os import path, fpathconf, fsync
import re
import signal
import traceback
import bisect

from codecs import open


def readfile(filename):
    with open(filename, encoding="utf-8") as f:
        return f.read()


__version__ = readfile(path.join(path.dirname(__file__), "VERSION"))
version_pat = re.compile(r"version (\d+(\.\d+)+)")


## To update this list, use
## >>> from pari_utils.parser import gp_functions
## >>> from textwrap import wrap
## >>> print('\n'.join(wrap(str(list(gp_functions()))[1:-1], initial_indent='    ', subsequent_indent='    ')))
gp_builtins = [
    "Catalan",
    "Col",
    "Colrev",
    "Euler",
    "I",
    "List",
    "Map",
    "Mat",
    "Mod",
    "O",
    "Pi",
    "Pol",
    "Polrev",
    "Qfb",
    "Ser",
    "Set",
    "Str",
    "Strchr",
    "Strexpand",
    "Strprintf",
    "Strtex",
    "Vec",
    "Vecrev",
    "Vecsmall",
    "abs",
    "acos",
    "acosh",
    "addhelp",
    "addprimes",
    "agm",
    "airy",
    "alarm",
    "algadd",
    "algalgtobasis",
    "algaut",
    "algb",
    "algbasis",
    "algbasistoalg",
    "algcenter",
    "algcentralproj",
    "algchar",
    "algcharpoly",
    "algdegree",
    "algdep",
    "algdim",
    "algdisc",
    "algdivl",
    "algdivr",
    "alggroup",
    "alggroupcenter",
    "alghasse",
    "alghassef",
    "alghassei",
    "algindex",
    "alginit",
    "alginv",
    "alginvbasis",
    "algisassociative",
    "algiscommutative",
    "algisdivision",
    "algisdivl",
    "algisinv",
    "algisramified",
    "algissemisimple",
    "algissimple",
    "algissplit",
    "alglatadd",
    "alglatcontains",
    "alglatelement",
    "alglathnf",
    "alglatindex",
    "alglatinter",
    "alglatlefttransporter",
    "alglatmul",
    "alglatrighttransporter",
    "alglatsubset",
    "algmakeintegral",
    "algmul",
    "algmultable",
    "algneg",
    "algnorm",
    "algpoleval",
    "algpow",
    "algprimesubalg",
    "algquotient",
    "algradical",
    "algramifiedplaces",
    "algrandom",
    "algrelmultable",
    "algsimpledec",
    "algsplit",
    "algsplittingdata",
    "algsplittingfield",
    "algsqr",
    "algsub",
    "algsubalg",
    "algtableinit",
    "algtensor",
    "algtomatrix",
    "algtrace",
    "algtype",
    "alias",
    "allocatemem",
    "apply",
    "arg",
    "arity",
    "asin",
    "asinh",
    "asympnum",
    "asympnumraw",
    "atan",
    "atanh",
    "bernfrac",
    "bernpol",
    "bernreal",
    "bernvec",
    "besselh1",
    "besselh2",
    "besseli",
    "besselj",
    "besseljh",
    "besselk",
    "besseln",
    "bessely",
    "bestappr",
    "bestapprPade",
    "bestapprnf",
    "bezout",
    "bezoutres",
    "bigomega",
    "binary",
    "binomial",
    "bitand",
    "bitneg",
    "bitnegimply",
    "bitor",
    "bitprecision",
    "bittest",
    "bitxor",
    "bnfcertify",
    "bnfdecodemodule",
    "bnfinit",
    "bnfisintnorm",
    "bnfisnorm",
    "bnfisprincipal",
    "bnfissunit",
    "bnfisunit",
    "bnflog",
    "bnflogdegree",
    "bnflogef",
    "bnfnarrow",
    "bnfsignunit",
    "bnfsunit",
    "bnfunits",
    "bnrL1",
    "bnrchar",
    "bnrclassfield",
    "bnrclassno",
    "bnrclassnolist",
    "bnrconductor",
    "bnrconductorofchar",
    "bnrdisc",
    "bnrdisclist",
    "bnrgaloisapply",
    "bnrgaloismatrix",
    "bnrinit",
    "bnrisconductor",
    "bnrisgalois",
    "bnrisprincipal",
    "bnrmap",
    "bnrrootnumber",
    "bnrstark",
    "break",
    "call",
    "ceil",
    "centerlift",
    "characteristic",
    "charconj",
    "chardiv",
    "chareval",
    "chargalois",
    "charker",
    "charmul",
    "charorder",
    "charpoly",
    "charpow",
    "chinese",
    "cmp",
    "component",
    "concat",
    "conj",
    "conjvec",
    "content",
    "contfrac",
    "contfraceval",
    "contfracinit",
    "contfracpnqn",
    "core",
    "coredisc",
    "cos",
    "cosh",
    "cotan",
    "cotanh",
    "default",
    "denominator",
    "deriv",
    "derivn",
    "derivnum",
    "diffop",
    "digits",
    "dilog",
    "dirdiv",
    "direuler",
    "dirmul",
    "dirpowers",
    "dirpowerssum",
    "dirzetak",
    "divisors",
    "divisorslenstra",
    "divrem",
    "eint1",
    "ellE",
    "ellK",
    "ellL1",
    "elladd",
    "ellak",
    "ellan",
    "ellanalyticrank",
    "ellap",
    "ellbil",
    "ellbsd",
    "ellcard",
    "ellchangecurve",
    "ellchangepoint",
    "ellchangepointinv",
    "ellconvertname",
    "elldivpol",
    "elleisnum",
    "elleta",
    "ellformaldifferential",
    "ellformalexp",
    "ellformallog",
    "ellformalpoint",
    "ellformalw",
    "ellfromeqn",
    "ellfromj",
    "ellgenerators",
    "ellglobalred",
    "ellgroup",
    "ellheegner",
    "ellheight",
    "ellheightmatrix",
    "ellidentify",
    "ellinit",
    "ellintegralmodel",
    "ellisdivisible",
    "ellisogeny",
    "ellisogenyapply",
    "ellisomat",
    "ellisoncurve",
    "ellisotree",
    "ellissupersingular",
    "ellj",
    "elllocalred",
    "elllog",
    "elllseries",
    "ellminimaldisc",
    "ellminimalmodel",
    "ellminimaltwist",
    "ellmoddegree",
    "ellmodulareqn",
    "ellmul",
    "ellneg",
    "ellnonsingularmultiple",
    "ellorder",
    "ellordinate",
    "ellpadicL",
    "ellpadicbsd",
    "ellpadicfrobenius",
    "ellpadicheight",
    "ellpadicheightmatrix",
    "ellpadiclambdamu",
    "ellpadiclog",
    "ellpadicregulator",
    "ellpadics2",
    "ellperiods",
    "ellpointtoz",
    "ellpow",
    "ellratpoints",
    "ellrootno",
    "ellsea",
    "ellsearch",
    "ellsigma",
    "ellsub",
    "elltamagawa",
    "elltaniyama",
    "elltatepairing",
    "elltors",
    "elltwist",
    "ellweilcurve",
    "ellweilpairing",
    "ellwp",
    "ellxn",
    "ellzeta",
    "ellztopoint",
    "erfc",
    "errname",
    "error",
    "eta",
    "eulerfrac",
    "eulerianpol",
    "eulerphi",
    "eulerpol",
    "eulervec",
    "eval",
    "exp",
    "expm1",
    "exponent",
    "export",
    "exportall",
    "extern",
    "externstr",
    "factor",
    "factorback",
    "factorcantor",
    "factorff",
    "factorial",
    "factorint",
    "factormod",
    "factormodDDF",
    "factormodSQF",
    "factornf",
    "factorpadic",
    "ffcompomap",
    "ffembed",
    "ffextend",
    "fffrobenius",
    "ffgen",
    "ffinit",
    "ffinvmap",
    "fflog",
    "ffmap",
    "ffmaprel",
    "ffnbirred",
    "fforder",
    "ffprimroot",
    "fft",
    "fftinv",
    "fibonacci",
    "fileclose",
    "fileextern",
    "fileflush",
    "fileopen",
    "fileread",
    "filereadstr",
    "filewrite",
    "filewrite1",
    "floor",
    "fold",
    "for",
    "forcomposite",
    "fordiv",
    "fordivfactored",
    "foreach",
    "forell",
    "forfactored",
    "forpart",
    "forperm",
    "forprime",
    "forprimestep",
    "forqfvec",
    "forsquarefree",
    "forstep",
    "forsubgroup",
    "forsubset",
    "forvec",
    "frac",
    "fromdigits",
    "galoischardet",
    "galoischarpoly",
    "galoischartable",
    "galoisconjclasses",
    "galoisexport",
    "galoisfixedfield",
    "galoisgetgroup",
    "galoisgetname",
    "galoisgetpol",
    "galoisidentify",
    "galoisinit",
    "galoisisabelian",
    "galoisisnormal",
    "galoispermtopol",
    "galoissubcyclo",
    "galoissubfields",
    "galoissubgroups",
    "gamma",
    "gammah",
    "gammamellininv",
    "gammamellininvasymp",
    "gammamellininvinit",
    "gcd",
    "gcdext",
    "genus2red",
    "getabstime",
    "getcache",
    "getenv",
    "getheap",
    "getlocalbitprec",
    "getlocalprec",
    "getrand",
    "getstack",
    "gettime",
    "getwalltime",
    "global",
    "halfgcd",
    "hammingweight",
    "hilbert",
    "hyperellcharpoly",
    "hyperellpadicfrobenius",
    "hyperellratpoints",
    "hypergeom",
    "hyperu",
    "idealadd",
    "idealaddtoone",
    "idealappr",
    "idealchinese",
    "idealcoprime",
    "idealdiv",
    "idealdown",
    "idealfactor",
    "idealfactorback",
    "idealfrobenius",
    "idealhnf",
    "idealintersect",
    "idealinv",
    "idealismaximal",
    "idealispower",
    "ideallist",
    "ideallistarch",
    "ideallog",
    "idealmin",
    "idealmul",
    "idealnorm",
    "idealnumden",
    "idealpow",
    "idealprimedec",
    "idealprincipalunits",
    "idealramgroups",
    "idealred",
    "idealredmodpower",
    "idealstar",
    "idealtwoelt",
    "idealval",
    "if",
    "iferr",
    "imag",
    "incgam",
    "incgamc",
    "inline",
    "input",
    "install",
    "intcirc",
    "intformal",
    "intfuncinit",
    "intnum",
    "intnumgauss",
    "intnumgaussinit",
    "intnuminit",
    "intnumromb",
    "isfundamental",
    "ispolygonal",
    "ispower",
    "ispowerful",
    "isprime",
    "isprimepower",
    "ispseudoprime",
    "ispseudoprimepower",
    "issquare",
    "issquarefree",
    "istotient",
    "kill",
    "kronecker",
    "lambertw",
    "laurentseries",
    "lcm",
    "length",
    "lex",
    "lfun",
    "lfunabelianrelinit",
    "lfunan",
    "lfunartin",
    "lfuncheckfeq",
    "lfunconductor",
    "lfuncost",
    "lfuncreate",
    "lfundiv",
    "lfundual",
    "lfunetaquo",
    "lfungenus2",
    "lfunhardy",
    "lfuninit",
    "lfunlambda",
    "lfunmf",
    "lfunmfspec",
    "lfunmul",
    "lfunorderzero",
    "lfunqf",
    "lfunrootres",
    "lfunshift",
    "lfunsympow",
    "lfuntheta",
    "lfunthetacost",
    "lfunthetainit",
    "lfuntwist",
    "lfunzeros",
    "lift",
    "liftall",
    "liftint",
    "liftpol",
    "limitnum",
    "lindep",
    "listcreate",
    "listinsert",
    "listkill",
    "listpop",
    "listput",
    "listsort",
    "lngamma",
    "local",
    "localbitprec",
    "localprec",
    "log",
    "log1p",
    "logint",
    "mapdelete",
    "mapget",
    "mapisdefined",
    "mapput",
    "matadjoint",
    "matalgtobasis",
    "matbasistoalg",
    "matcompanion",
    "matconcat",
    "matdet",
    "matdetint",
    "matdetmod",
    "matdiagonal",
    "mateigen",
    "matfrobenius",
    "mathess",
    "mathilbert",
    "mathnf",
    "mathnfmod",
    "mathnfmodid",
    "mathouseholder",
    "matid",
    "matimage",
    "matimagecompl",
    "matimagemod",
    "matindexrank",
    "matintersect",
    "matinverseimage",
    "matinvmod",
    "matisdiagonal",
    "matker",
    "matkerint",
    "matkermod",
    "matmuldiagonal",
    "matmultodiagonal",
    "matpascal",
    "matpermanent",
    "matqr",
    "matrank",
    "matreduce",
    "matrix",
    "matrixqz",
    "matsize",
    "matsnf",
    "matsolve",
    "matsolvemod",
    "matsupplement",
    "mattranspose",
    "max",
    "mfDelta",
    "mfEH",
    "mfEk",
    "mfTheta",
    "mfatkin",
    "mfatkineigenvalues",
    "mfatkininit",
    "mfbasis",
    "mfbd",
    "mfbracket",
    "mfcoef",
    "mfcoefs",
    "mfconductor",
    "mfcosets",
    "mfcuspisregular",
    "mfcusps",
    "mfcuspval",
    "mfcuspwidth",
    "mfderiv",
    "mfderivE2",
    "mfdescribe",
    "mfdim",
    "mfdiv",
    "mfeigenbasis",
    "mfeigensearch",
    "mfeisenstein",
    "mfembed",
    "mfeval",
    "mffields",
    "mffromell",
    "mffrometaquo",
    "mffromlfun",
    "mffromqf",
    "mfgaloisprojrep",
    "mfgaloistype",
    "mfhecke",
    "mfheckemat",
    "mfinit",
    "mfisCM",
    "mfisequal",
    "mfisetaquo",
    "mfkohnenbasis",
    "mfkohnenbijection",
    "mfkohneneigenbasis",
    "mflinear",
    "mfmanin",
    "mfmul",
    "mfnumcusps",
    "mfparams",
    "mfperiodpol",
    "mfperiodpolbasis",
    "mfpetersson",
    "mfpow",
    "mfsearch",
    "mfshift",
    "mfshimura",
    "mfslashexpansion",
    "mfspace",
    "mfsplit",
    "mfsturm",
    "mfsymbol",
    "mfsymboleval",
    "mftaylor",
    "mftobasis",
    "mftocoset",
    "mftonew",
    "mftraceform",
    "mftwist",
    "min",
    "minpoly",
    "modreverse",
    "moebius",
    "msatkinlehner",
    "mscosets",
    "mscuspidal",
    "msdim",
    "mseisenstein",
    "mseval",
    "msfarey",
    "msfromcusp",
    "msfromell",
    "msfromhecke",
    "msgetlevel",
    "msgetsign",
    "msgetweight",
    "mshecke",
    "msinit",
    "msissymbol",
    "mslattice",
    "msnew",
    "msomseval",
    "mspadicL",
    "mspadicinit",
    "mspadicmoments",
    "mspadicseries",
    "mspathgens",
    "mspathlog",
    "mspetersson",
    "mspolygon",
    "msqexpansion",
    "mssplit",
    "msstar",
    "mstooms",
    "my",
    "newtonpoly",
    "next",
    "nextprime",
    "nfalgtobasis",
    "nfbasis",
    "nfbasistoalg",
    "nfcertify",
    "nfcompositum",
    "nfdetint",
    "nfdisc",
    "nfdiscfactors",
    "nfeltadd",
    "nfeltdiv",
    "nfeltdiveuc",
    "nfeltdivmodpr",
    "nfeltdivrem",
    "nfeltembed",
    "nfeltmod",
    "nfeltmul",
    "nfeltmulmodpr",
    "nfeltnorm",
    "nfeltpow",
    "nfeltpowmodpr",
    "nfeltreduce",
    "nfeltreducemodpr",
    "nfeltsign",
    "nfelttrace",
    "nfeltval",
    "nffactor",
    "nffactorback",
    "nffactormod",
    "nfgaloisapply",
    "nfgaloisconj",
    "nfgrunwaldwang",
    "nfhilbert",
    "nfhnf",
    "nfhnfmod",
    "nfinit",
    "nfisideal",
    "nfisincl",
    "nfisisom",
    "nfislocalpower",
    "nfkermodpr",
    "nfmodpr",
    "nfmodprinit",
    "nfmodprlift",
    "nfnewprec",
    "nfpolsturm",
    "nfroots",
    "nfrootsof1",
    "nfsnf",
    "nfsolvemodpr",
    "nfsplitting",
    "nfsubfields",
    "nfsubfieldscm",
    "nfsubfieldsmax",
    "norm",
    "norml2",
    "normlp",
    "numbpart",
    "numdiv",
    "numerator",
    "numtoperm",
    "omega",
    "oo",
    "padicappr",
    "padicfields",
    "padicprec",
    "parapply",
    "pareval",
    "parfor",
    "parforeach",
    "parforprime",
    "parforprimestep",
    "parforvec",
    "parploth",
    "parplothexport",
    "parselect",
    "parsum",
    "partitions",
    "parvector",
    "permcycles",
    "permorder",
    "permsign",
    "permtonum",
    "plot",
    "plotbox",
    "plotclip",
    "plotcolor",
    "plotcopy",
    "plotcursor",
    "plotdraw",
    "plotexport",
    "ploth",
    "plothexport",
    "plothraw",
    "plothrawexport",
    "plothsizes",
    "plotinit",
    "plotkill",
    "plotlines",
    "plotlinetype",
    "plotmove",
    "plotpoints",
    "plotpointsize",
    "plotpointtype",
    "plotrbox",
    "plotrecth",
    "plotrecthraw",
    "plotrline",
    "plotrmove",
    "plotrpoint",
    "plotscale",
    "plotstring",
    "polchebyshev",
    "polclass",
    "polcoef",
    "polcoeff",
    "polcompositum",
    "polcyclo",
    "polcyclofactors",
    "poldegree",
    "poldisc",
    "poldiscfactors",
    "poldiscreduced",
    "polgalois",
    "polgraeffe",
    "polhensellift",
    "polhermite",
    "polinterpolate",
    "poliscyclo",
    "poliscycloprod",
    "polisirreducible",
    "pollaguerre",
    "pollead",
    "pollegendre",
    "polmodular",
    "polrecip",
    "polred",
    "polredabs",
    "polredbest",
    "polredord",
    "polresultant",
    "polresultantext",
    "polroots",
    "polrootsbound",
    "polrootsff",
    "polrootsmod",
    "polrootspadic",
    "polrootsreal",
    "polsturm",
    "polsubcyclo",
    "polsylvestermatrix",
    "polsym",
    "poltchebi",
    "polteichmuller",
    "poltschirnhaus",
    "polylog",
    "polylogmult",
    "polzagier",
    "powers",
    "precision",
    "precprime",
    "prime",
    "primecert",
    "primecertexport",
    "primecertisvalid",
    "primepi",
    "primes",
    "print",
    "print1",
    "printf",
    "printp",
    "printsep",
    "printsep1",
    "printtex",
    "prod",
    "prodeuler",
    "prodeulerrat",
    "prodinf",
    "prodnumrat",
    "psdraw",
    "psi",
    "psploth",
    "psplothraw",
    "qfauto",
    "qfautoexport",
    "qfbclassno",
    "qfbcompraw",
    "qfbhclassno",
    "qfbil",
    "qfbnucomp",
    "qfbnupow",
    "qfbpowraw",
    "qfbprimeform",
    "qfbred",
    "qfbredsl2",
    "qfbsolve",
    "qfeval",
    "qfgaussred",
    "qfisom",
    "qfisominit",
    "qfjacobi",
    "qflll",
    "qflllgram",
    "qfminim",
    "qfnorm",
    "qforbits",
    "qfparam",
    "qfperfection",
    "qfrep",
    "qfsign",
    "qfsolve",
    "quadclassunit",
    "quaddisc",
    "quadgen",
    "quadhilbert",
    "quadpoly",
    "quadray",
    "quadregulator",
    "quadunit",
    "ramanujantau",
    "random",
    "randomprime",
    "read",
    "readstr",
    "readvec",
    "real",
    "removeprimes",
    "return",
    "rnfalgtobasis",
    "rnfbasis",
    "rnfbasistoalg",
    "rnfcharpoly",
    "rnfconductor",
    "rnfdedekind",
    "rnfdet",
    "rnfdisc",
    "rnfeltabstorel",
    "rnfeltdown",
    "rnfeltnorm",
    "rnfeltreltoabs",
    "rnfelttrace",
    "rnfeltup",
    "rnfequation",
    "rnfhnfbasis",
    "rnfidealabstorel",
    "rnfidealdown",
    "rnfidealfactor",
    "rnfidealhnf",
    "rnfidealmul",
    "rnfidealnormabs",
    "rnfidealnormrel",
    "rnfidealprimedec",
    "rnfidealreltoabs",
    "rnfidealtwoelt",
    "rnfidealup",
    "rnfinit",
    "rnfisabelian",
    "rnfisfree",
    "rnfislocalcyclo",
    "rnfisnorm",
    "rnfisnorminit",
    "rnfkummer",
    "rnflllgram",
    "rnfnormgroup",
    "rnfpolred",
    "rnfpolredabs",
    "rnfpolredbest",
    "rnfpseudobasis",
    "rnfsteinitz",
    "rootsof1",
    "round",
    "select",
    "self",
    "seralgdep",
    "serchop",
    "serconvol",
    "serlaplace",
    "serprec",
    "serreverse",
    "setbinop",
    "setintersect",
    "setisset",
    "setminus",
    "setrand",
    "setsearch",
    "setunion",
    "shift",
    "shiftmul",
    "sigma",
    "sign",
    "simplify",
    "sin",
    "sinc",
    "sinh",
    "sizebyte",
    "sizedigit",
    "solve",
    "solvestep",
    "sqr",
    "sqrt",
    "sqrtint",
    "sqrtn",
    "sqrtnint",
    "stirling",
    "strchr",
    "strexpand",
    "strjoin",
    "strprintf",
    "strsplit",
    "strtex",
    "strtime",
    "subgrouplist",
    "subst",
    "substpol",
    "substvec",
    "sum",
    "sumalt",
    "sumdedekind",
    "sumdigits",
    "sumdiv",
    "sumdivmult",
    "sumeulerrat",
    "sumformal",
    "suminf",
    "sumnum",
    "sumnumap",
    "sumnumapinit",
    "sumnuminit",
    "sumnumlagrange",
    "sumnumlagrangeinit",
    "sumnummonien",
    "sumnummonieninit",
    "sumnumrat",
    "sumpos",
    "system",
    "tan",
    "tanh",
    "taylor",
    "teichmuller",
    "theta",
    "thetanullk",
    "thue",
    "thueinit",
    "trace",
    "trap",
    "truncate",
    "type",
    "unexport",
    "unexportall",
    "uninline",
    "until",
    "valuation",
    "varhigher",
    "variable",
    "variables",
    "varlower",
    "vecextract",
    "vecmax",
    "vecmin",
    "vecprod",
    "vecsearch",
    "vecsort",
    "vecsum",
    "vector",
    "vectorsmall",
    "vectorv",
    "version",
    "warning",
    "weber",
    "while",
    "write",
    "write1",
    "writebin",
    "writetex",
    "zeta",
    "zetahurwitz",
    "zetamult",
    "zetamultall",
    "zetamultconvert",
    "zetamultdual",
    "znchar",
    "zncharconductor",
    "znchardecompose",
    "znchargauss",
    "zncharinduce",
    "zncharisodd",
    "znchartokronecker",
    "znchartoprimitive",
    "znconreychar",
    "znconreyconductor",
    "znconreyexp",
    "znconreylog",
    "zncoppersmith",
    "znlog",
    "znorder",
    "znprimroot",
    "znstar",
]


class GPKernel(Kernel):
    implementation = "gp_kernel"
    implementation_version = __version__
    _prompt = ">PEXPECT_PROMPT<"

    language_info = {
        "name": "gp",
        "codemirror_mode": "c",
        "mimetype": "text/x-gp",
        "file_extension": ".g",
    }

    def debug(self, message):
        return
        self.send_response(
            self.iopub_socket,
            "stream",
            {
                "name": "stdout",
                "text": f"DEBUG: {message}\n",
            },
        )

    def __init__(self, **kwargs):
        Kernel.__init__(self, **kwargs)
        # sets child, banner, language_info, language_version

        self._start_gp()

    def _start_gp(self):
        # Signal handlers are inherited by forked processes, and we can't easily
        # reset it from the subprocess. Since kernelapp ignores SIGINT except in
        # message handlers, we need to temporarily reset the SIGINT handler here
        # so that gp and its children are interruptible.
        sig = signal.signal(signal.SIGINT, signal.SIG_DFL)
        try:
            gp = spawn(
                f"gp -D prompt='{self._prompt}' -D breakloop=0 -D colors='no,no,no,no,no,no,no' -D readline=0",
                echo=False,
                encoding="utf-8",
                maxread=4194304,
                ignore_sighup=True,
                codec_errors="ignore",
            )
            gp.expect_exact(self._prompt)
            banner = gp.before
            self.child = gp
        finally:
            signal.signal(signal.SIGINT, sig)

        self.max_input_line_size = 255
        lang_version = re.search(
            r" GP/PARI CALCULATOR Version (\d*.\d*.\d*)", banner
        ).group(1)
        self.banner = "GP kernel connected to GP " + lang_version
        self.language_info["version"] = lang_version
        self.language_version = lang_version

    def do_execute(
        self, code, silent, store_history=True, user_expressions=None, allow_stdin=False
    ):
        code = code.rstrip()

        if not code.lstrip():
            return {
                "status": "ok",
                "execution_count": self.execution_count,
                "payload": [],
                "user_expressions": {},
            }

        interrupted = False

        read_characters = [0]

        def wait_for_output(read_characters, filename=None):
            # this function will *modify* the read_characters[0]
            # handle error messages with filename
            # output output initially on intervals of 0.5 seconds
            # If no output is received, the interval slowly increases to 30 seconds over 5 min
            initial_counter = counter = 10
            initial_timeout = timeout = 0.1

            while True:
                v = self.child.expect_exact([self._prompt, TIMEOUT], timeout=timeout)

                # something in output
                if not silent and len(self.child.before) > read_characters[0]:
                    output = self.child.before[read_characters[0] :]

                    if filename:
                        match = re.search(
                            r'  \*\*\*   at top-level: read\(".+\n  \*\*\*\s+\^-+\s+\n  \*\*\*\s+in function read:',
                            output,
                        )
                        self.debug(repr(output))
                        if match:
                            begin, end = match.span()
                            # hide the fact that we read a temporary file
                            output = (
                                output[0:begin]
                                + "  ***   at top-level:    "
                                + output[end:]
                            )

                    if output:
                        self.send_response(
                            self.iopub_socket,
                            "stream",
                            {
                                "name": "stdout",
                                "text": output,
                            },
                        )
                    read_characters[0] = len(self.child.before)
                    counter = initial_counter
                    timeout = initial_timeout
                counter -= 1
                # increase timeout after default_counter attempts of processing line
                if counter <= 0:
                    # timeout = min(30, 2 * timeout)
                    counter = initial_counter
                if v == 0:
                    # finished waiting for output
                    return

        append_to_output = ""

        self.debug("before try")
        self.debug(f"{len(code)} {self.max_input_line_size}")
        try:
            # if the code block is long write it into a file and load it in gp
            # this takes about as the same time as sending a single line, and thus
            # we check the length of the whole code block
            # WARNING: the more obvious workaround of splitting each long line into
            # several small escaped lines, doesn't work, as we hit other system limits.
            # For example, I wasn't able to send a line longer that 2^16 character.
            if len(code) > self.max_input_line_size:
                # send the line via a temporary file
                with NamedTemporaryFile("w+t") as tmpfile:

                    self.debug(tmpfile.name)
                    tmpfile.write(code)
                    tmpfile.flush()
                    fsync(tmpfile.fileno())
                    self.child.sendline(f'read("{tmpfile.name}");')
                    wait_for_output(read_characters, tmpfile.name)
            else:
                self.child.sendline(code)
                wait_for_output(read_characters)
        except KeyboardInterrupt:
            self.debug("KeyboardInterrupt")
            self.child.sendintr()
            interrupted = True
            wait_for_output(read_characters)
            append_to_output = "Interrupted"
        except EOF:
            self.debug("EOF")
            append_to_output = "Restarting GP"
            self._start_gp()
        self.debug("end of try block")

        if not silent:
            # Send standard output
            self.send_response(
                self.iopub_socket,
                "stream",
                {
                    "name": "stdout",
                    "text": self.child.before[read_characters[0] :] + append_to_output,
                },
            )

        if interrupted:
            return {"status": "abort", "execution_count": self.execution_count}

        return {
            "status": "ok",
            "execution_count": self.execution_count,
            "payload": [],
            "user_expressions": {},
        }

    def do_complete(self, code, cursor_pos):
        code = code[:cursor_pos]
        default = {
            "matches": [],
            "cursor_start": 0,
            "cursor_end": cursor_pos,
            "metadata": dict(),
            "status": "ok",
        }
        if not code or code[-1] == " ":
            return default

        # get last token
        token = code[:cursor_pos]
        for sep in ["\n", ";", " "]:  # we just need the last chunk
            token = token.rpartition(sep)[-1]
        if not token:
            return default
        start = cursor_pos - len(token)

        low = bisect.bisect_left(gp_builtins, token)
        # very hacky
        high = bisect.bisect_right(gp_builtins, token + chr(127), low)
        matches = gp_builtins[low:high]

        if not matches:
            return default

        return {
            "matches": matches,
            "cursor_start": start,
            "cursor_end": cursor_pos,
            "metadata": dict(),
            "status": "ok",
        }
