from ..mdx_parser import binary_reader
from ... import constants


def parse_version(data: bytes):
    r = binary_reader.Reader(data)
    version = r.getf('<I')[0]

    if version not in constants.MDX_VERSIONS:
        # Every field is gated on "version >= n", so an unlisted version still reads correctly as long as it
        # adds nothing new. Newer than we know is the risky case, read it as the latest we know.
        known = max((v for v in constants.MDX_VERSIONS if v <= version), default=constants.MDX_VERSIONS[0])
        print("Version %s is not supported; the model will load as %s which might cause issues"
              % (version, known))
        version = known
    constants.MDX_CURRENT_VERSION = version
    return version
