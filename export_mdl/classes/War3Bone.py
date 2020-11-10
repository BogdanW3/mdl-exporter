from .War3Object import War3Object


class War3Bone(War3Object):
    def __unit__(self, obj, model):
        War3Object.__init__(self, obj.name)
        model.objects['bone'].add(self)
