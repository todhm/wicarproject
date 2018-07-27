import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from carapi.carbooking_tests import CarBookingApiTest
from carapi.carupload_tests import CaruploadTest
from carapi.userinfo_tests import UserInfoTest
from caruser.tests import UserTest
from carbooking.tests import CarBookingTest
from carupload.tests import CarUploadViewTest
from wicaradmin.tests import AdminPageTest
from utilities.tests import UtilTest
from utilities.dao.daotests import DaoTest
if __name__ == "__main__":
    unittest.main()
