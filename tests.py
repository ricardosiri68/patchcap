from nose.tools import timed
from platefinder import PlateFinder
from patchfinder import PatchFinder
from SimpleCV import Image

class TestPatchCap:
 
    def setup(self):
        pass

    def teardown(self):
        pass
 
    @classmethod
    def setup_class(cls):
        pass
 
    @classmethod
    def teardown_class(cls):
        pass
 

    def test_oks(self):
        finder = PlateFinder()
        oks=['images/lyd134-1.jpg','images/krq809.jpg','images/krq809-1.jpg']
        for p in oks:
            plate = finder.find(Image(p))
            assert plate


    @timed(0.5)
    def test_velocity(self):
        pass
