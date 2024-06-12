MDX_VERSIONS = [800, 900, 1000, 1100]
MDL_VERSIONS = [800, 900, 1000]
MDX_CURRENT_VERSION = 800
# MDX FILE CHUNKS
CHUNK_MDX_MODEL                 = 'MDLX'
# MDX MODEL SUB-CHUNKS
CHUNK_VERSION                   = 'VERS'
CHUNK_MODEL                     = 'MODL'
CHUNK_SEQUENCE                  = 'SEQS'
CHUNK_GLOBAL_SEQUENCE           = 'GLBS'
CHUNK_MATERIAL                  = 'MTLS'
CHUNK_TEXTURE                   = 'TEXS'
CHUNK_TEXTURE_ANIMATIONS        = 'TXAN'
CHUNK_GEOSET                    = 'GEOS'
CHUNK_GEOSET_ANIMATION          = 'GEOA'
CHUNK_BONE                      = 'BONE'
CHUNK_LIGHT                     = 'LITE'
CHUNK_HELPER                    = 'HELP'
CHUNK_ATTACHMENT                = 'ATCH'
CHUNK_PIVOT_POINT               = 'PIVT'
CHUNK_PARTICLE_EM               = 'PREM'
CHUNK_PARTICLE_EM2              = 'PRE2'
CHUNK_POPCORN                   = 'CORN'
CHUNK_RIBBON_EM                 = 'RIBB'
CHUNK_CAMERAS                   = 'CAMS'
CHUNK_EVENT_OBJECT              = 'EVTS'
CHUNK_COLLISION_SHAPE           = 'CLID'
CHUNK_FACE_FX                   = 'FAFX'
CHUNK_BIND_POSE                 = 'BPOS'
# TEXTURE ANIMATION SUB-CHUNKS
CHUNK_TEX_ANIM_TRANSLATION      = 'KTAT'  # (MdlUtils.TOKEN_TRANSLATION, MdlxTimelineType.VECTOR3_TIMELINE),
CHUNK_TEX_ANIM_ROTATION         = 'KTAR'  # (MdlUtils.TOKEN_ROTATION, MdlxTimelineType.VECTOR4_TIMELINE),
CHUNK_TEX_ANIM_SCALING          = 'KTAS'  # (MdlUtils.TOKEN_SCALING, MdlxTimelineType.VECTOR3_TIMELINE),
# GEOSET SUB-CHUNKS
CHUNK_VERTEX_POSITION           = 'VRTX'
CHUNK_VERTEX_NORMAL             = 'NRMS'
CHUNK_FACE_TYPE_GROUP           = 'PTYP'
CHUNK_FACE_GROUP                = 'PCNT'
CHUNK_FACE                      = 'PVTX'
CHUNK_VERTEX_GROUP              = 'GNDX'
CHUNK_MATRIX_GROUP              = 'MTGC'
CHUNK_MATRIX_INDEX              = 'MATS'
CHUNK_TANGENTS                  = 'TANG'
CHUNK_SKIN                      = 'SKIN'
CHUNK_TEXTURE_VERTEX_GROUP      = 'UVAS'
CHUNK_VERTEX_TEXTURE_POSITION   = 'UVBS'
# MATERIAL SUB-CHUNKS
CHUNK_LAYER                     = 'LAYS'
# LAYER ANIMATED SUB-CHUNKS
CHUNK_MATERIAL_TEXTURE_ID       = 'KMTF'
CHUNK_MATERIAL_ALPHA            = 'KMTA'
CHUNK_MATERIAL_EMISSIONS        = 'KMTE'
CHUNK_MATERIAL_FRESNEL_COLOR    = 'KFC3'
CHUNK_MATERIAL_FRESNEL_ALPHA    = 'KFCA'
CHUNK_MATERIAL_FRESNEL_TEAMCOLOR = 'KFTC'
# NODE ANIMATED SUB-CHUNKS
CHUNK_GEOSET_TRANSLATION        = 'KGTR'
CHUNK_GEOSET_ROTATION           = 'KGRT'
CHUNK_GEOSET_SCALING            = 'KGSC'
# ATTACHMENT ANIMATED SUB-CHUNKS
CHUNK_ATTACHMENT_VISIBILITY     = 'KATV'
# EVENT OBJECT ANIMATED SUB-CHUNKS
CHUNK_EVENT_TRACKS              = 'KEVT'
# GEOSET ANIMATION SUB-CHUNKS
CHUNK_GEOSET_COLOR              = 'KGAC'
CHUNK_GEOSET_ALPHA              = 'KGAO'
# LIGHT ANIMATION SUB-CHUNKS
CHUNK_LIGHT_ATTENUATION_START   = 'KLAS'  # (MdlUtils.TOKEN_ATTENUATION_START, MdlxTimelineType.FLOAT_TIMELINE),
CHUNK_LIGHT_ATTENUATION_END     = 'KLAE'  # (MdlUtils.TOKEN_ATTENUATION_END, MdlxTimelineType.FLOAT_TIMELINE),
CHUNK_LIGHT_COLOR               = 'KLAC'  # (MdlUtils.TOKEN_COLOR, MdlxTimelineType.VECTOR3_TIMELINE),
CHUNK_LIGHT_INTENSITY           = 'KLAI'  # (MdlUtils.TOKEN_INTENSITY, MdlxTimelineType.FLOAT_TIMELINE),
CHUNK_LIGHT_AMBIENT_INTENSITY   = 'KLBI'  # (MdlUtils.TOKEN_AMB_INTENSITY, MdlxTimelineType.FLOAT_TIMELINE),
CHUNK_LIGHT_AMBIENT_COLOR       = 'KLBC'  # (MdlUtils.TOKEN_AMB_COLOR, MdlxTimelineType.VECTOR3_TIMELINE),
CHUNK_LIGHT_VISIBILITY          = 'KLAV'  # (MdlUtils.TOKEN_VISIBILITY, MdlxTimelineType.FLOAT_TIMELINE),
# SUB-CHUNKS
SUB_CHUNKS_MDX_MODEL = (
    CHUNK_VERSION,
    CHUNK_GEOSET,
    CHUNK_TEXTURE,
    CHUNK_MATERIAL,
    CHUNK_MODEL,
    CHUNK_BONE,
    CHUNK_LIGHT,
    CHUNK_PIVOT_POINT,
    CHUNK_HELPER,
    CHUNK_ATTACHMENT,
    CHUNK_EVENT_OBJECT,
    CHUNK_COLLISION_SHAPE,
    CHUNK_SEQUENCE,
    CHUNK_GLOBAL_SEQUENCE,
    CHUNK_GEOSET_ANIMATION,
    CHUNK_PARTICLE_EM,
    CHUNK_PARTICLE_EM2,
    CHUNK_POPCORN,
    CHUNK_RIBBON_EM,
    CHUNK_CAMERAS,
    CHUNK_FACE_FX,
    CHUNK_BIND_POSE
    )
SUB_CHUNKS_LAYER = (
    CHUNK_MATERIAL_TEXTURE_ID,
    CHUNK_MATERIAL_ALPHA,
    CHUNK_MATERIAL_EMISSIONS,
    CHUNK_MATERIAL_FRESNEL_COLOR,
    CHUNK_MATERIAL_FRESNEL_ALPHA,
    CHUNK_MATERIAL_FRESNEL_TEAMCOLOR
    )
SUB_CHUNKS_GEOSET_ANIMATION = (
    CHUNK_GEOSET_COLOR,
    CHUNK_GEOSET_ALPHA
    )
SUB_CHUNKS_NODE = (
    CHUNK_GEOSET_TRANSLATION,
    CHUNK_GEOSET_ROTATION,
    CHUNK_GEOSET_SCALING
    )
SUB_CHUNKS_TEX_ANIM = (
    CHUNK_TEX_ANIM_TRANSLATION,
    CHUNK_TEX_ANIM_ROTATION,
    CHUNK_TEX_ANIM_SCALING
    )
SUB_CHUNKS_LIGHT = (
    CHUNK_LIGHT_ATTENUATION_START,
    CHUNK_LIGHT_ATTENUATION_END,
    CHUNK_LIGHT_COLOR,
    CHUNK_LIGHT_INTENSITY,
    CHUNK_LIGHT_AMBIENT_INTENSITY,
    CHUNK_LIGHT_AMBIENT_COLOR,
    CHUNK_LIGHT_VISIBILITY
    )
# INTERPOLATION TYPES
INTERPOLATION_TYPE_NONE = 0
INTERPOLATION_TYPE_LINEAR = 1
INTERPOLATION_TYPE_HERMITE = 2
INTERPOLATION_TYPE_BEZIER = 3
INTERPOLATION_TYPE_BLEND_NAMES = {
    0: 'CONSTANT',
    1: 'LINEAR',
    2: 'BEZIER',
    3: 'BEZIER'
    }
INTERPOLATION_NAME_BLEND_NAME = {
    'DontInterp': 'CONSTANT',
    'Linear': 'LINEAR',
    'Hermite': 'BEZIER',
    'Bezier': 'BEZIER'
}
INTERPOLATION_TYPE_NUMBERS = {
    'DontInterp': 0,
    'Linear': 1,
    'Hermite': 2,
    'Bezier': 3
}
INTERPOLATION_TYPE_MDL_NAMES = {
    0: 'DontInterp',
    1: 'Linear',
    2: 'Hermite',
    3: 'Bezier'
    }
# TEAM COLORS
TEAM_COLORS = [
    (1.000000, 0.011765, 0.011765), # Red
    (0.000000, 0.258824, 1.000000), # Blue
    (0.105882, 0.905882, 0.729412), # Teal
    (0.333333, 0.000000, 0.505882), # Purple
    (0.996078, 0.988235, 0.000000), # Yellow
    (0.996078, 0.537255, 0.050980), # Orange
    (0.129412, 0.749020, 0.000000), # Green
    (0.894118, 0.360784, 0.686275), # Pink
    (0.576471, 0.584314, 0.588235), # Gray
    (0.494118, 0.749020, 0.945098), # Light Blue
    (0.062745, 0.384314, 0.278431), # Dark Green
    (0.309804, 0.168627, 0.019608), # Brown
    
    (0.611765, 0.000000, 0.000000), # Maroon
    (0.000000, 0.000000, 0.764706), # Navy
    (0.000000, 0.921569, 1.000000), # Turquoise
    (0.741176, 0.000000, 1.000000), # Violet
    (0.925490, 0.807843, 0.529412), # Wheat
    (0.968627, 0.647059, 0.545098), # Peach
    (0.749020, 1.000000, 0.505882), # Mint
    (0.858824, 0.721569, 0.921569), # Lavender
    (0.309804, 0.313725, 0.333333), # Coal
    (0.925490, 0.941176, 1.000000), # Snow
    (0.000000, 0.470588, 0.117647), # Emerald
    (0.647059, 0.435294, 0.203922), # Peanut

    (0.180392, 0.176471, 0.180392)  # Black
]

TEAM_COLOR_IMAGE_PATH = 'ReplaceableTextures\\TeamColor\\TeamColor'
TEAM_GLOW_IMAGE_PATH = 'ReplaceableTextures\\TeamGlow\\TeamGlow'
TEAM_IMAGE_EXT = '.dds'

FILTER_MODES = {
    0: 'None',
    1: 'Transparent',
    2: 'Blend',
    3: 'Additive',
    4: 'AddAlpha',
    5: 'Modulate',
    6: 'Modulate2x'
}

def get_team_color(teamColorIndex):
    return TEAM_COLOR_IMAGE_PATH + '{0:0>2}'.format(teamColorIndex) + TEAM_IMAGE_EXT


def get_team_glow(teamGlowIndex):
    return TEAM_GLOW_IMAGE_PATH + '{0:0>2}'.format(teamGlowIndex) + TEAM_IMAGE_EXT

ENCODINGS = {
    'LATIN_1': 'latin-1',
    'UTF_8': 'utf-8',
    'UTF_16': 'utf-16',
    'UTF_32': 'utf-32',
    'ASCII': 'ascii',
    'BIG5': 'big5',
    'EUC_KR': 'euc_kr',
    'EUC_JP': 'euc_jp',
}
