from .mdl_reader import extract_bracket_content
from ... import constants


def parse_version(data: str) -> int:
    version_data_internal = extract_bracket_content(data)
    version = int(version_data_internal.replace(",", "").split(" ")[1].strip())
    print("mdl version: ", version)
    if version in constants.MDX_VERSIONS:
        constants.MDX_CURRENT_VERSION = version
        return version
    else:
        print("Version %s is not supported; the model will load as %s which might cause issues"
              % (version, 800))
        # raise Exception('unsupported MDX format version: {0}'.format(version))
        return 800
