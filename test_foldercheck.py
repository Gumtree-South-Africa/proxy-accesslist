from foldercheck import foldertest

stuff = foldertest.squidcheck('./test_data/gooddata')

def test_squidlayout():
    stuff.check()


