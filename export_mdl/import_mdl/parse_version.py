def parse_version(data):
    version = data.replace(",", "").split(" ")[1]
    print("mdl version: ", version)
    if version != 800:
        raise Exception('unsupported MDX format version: {0}'.format(version))
