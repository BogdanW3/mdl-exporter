from .mdl_reader import extract_bracket_content
from ... import constants


def parse_version(data: str) -> int:
    version_data_internal = extract_bracket_content(data)
    version = int(version_data_internal.replace(",", "").split(" ")[1].strip())
    print("mdl version: ", version)
    if version not in constants.MDL_VERSIONS:
        known = max((v for v in constants.MDL_VERSIONS if v <= version), default=constants.MDL_VERSIONS[0])
        print("Version %s is not supported; the model will load as %s which might cause issues"
              % (version, known))
        version = known
    constants.MDX_CURRENT_VERSION = version
    return version
