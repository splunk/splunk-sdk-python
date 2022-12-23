from .ReadOnlyCollection import ReadOnlyCollection


class CollectionTest(ReadOnlyCollection):

    def create(self):
        print("val is ", self.val)
