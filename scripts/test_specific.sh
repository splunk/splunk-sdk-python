echo "To run a specific test:"
echo "  tox -e py37,py39 [test_file_path]::[TestClassName]::[test_method]"
echo "For Example, To run 'test_autologin' testcase from 'test_service.py' file run"
echo "  tox -e py37 -- tests/test_service.py::ServiceTestCase::test_autologin"
