import shutil
from pathlib import Path
from unittest import mock

import pytest

from foldercheck import foldertest


class TestFolderCheck:
    def test_squidlayout(self, tmp_path_factory):
        fn = tmp_path_factory.mktemp("good", numbered=False)
        for folder in ["prod", "nonprod"]:
            Path.mkdir(Path.joinpath(fn, f"cloud/{folder}"), parents=True)
            with open(
                Path.joinpath(fn, f"cloud/{folder}/domains-allowlist"), "w"
            ) as fh:
                fh.write(".domain.com # a domain\n.anotherdomain.com")
            with open(Path.joinpath(fn, f"cloud/{folder}/ips-allowlist"), "w") as fh:
                fh.write("192.168.0.0/24 # a prefix\n192.169.0.1 # a single ip")

        with open(Path.joinpath(fn, "denylist"), "w") as fh:
            fh.write("# deny")

        stuff = foldertest.squidcheck(fn)
        stuff.check()
        shutil.rmtree(fn)

    def test_squidlayout_extra_folder(self, tmp_path_factory):
        fn = tmp_path_factory.mktemp("good", numbered=False)
        for folder in ["prod", "nonprod"]:
            Path.mkdir(Path.joinpath(fn, f"cloud/{folder}"), parents=True)
            with open(
                Path.joinpath(fn, f"cloud/{folder}/domains-allowlist"), "w"
            ) as fh:
                fh.write(".domain.com # a domain\n.anotherdomain.com")
            with open(Path.joinpath(fn, f"cloud/{folder}/ips-allowlist"), "w") as fh:
                fh.write("192.168.0.0/24 # a prefix\n192.169.0.1 # a single ip")

        with open(Path.joinpath(fn, "denylist"), "w") as fh:
            fh.write("# deny")
        Path.mkdir(Path.joinpath(fn, "cloud/unknown"), parents=True)
        Path.mkdir(Path.joinpath(fn, ".git"), parents=True)

        stuff = foldertest.squidcheck(fn)
        with pytest.raises(SystemExit):
            stuff.check()

        shutil.rmtree(fn)

    def test_squidlayout_extra_file(self, tmp_path_factory):
        fn = tmp_path_factory.mktemp("good", numbered=False)
        for folder in ["prod", "nonprod"]:
            Path.mkdir(Path.joinpath(fn, f"cloud/{folder}"), parents=True)
            with open(
                Path.joinpath(fn, f"cloud/{folder}/domains-allowlist"), "w"
            ) as fh:
                fh.write(".domain.com # a domain\n.anotherdomain.com")
            with open(Path.joinpath(fn, f"cloud/{folder}/ips-allowlist"), "w") as fh:
                fh.write("192.168.0.0/24 # a prefix\n192.169.0.1 # a single ip")

        with open(Path.joinpath(fn, "denylist"), "w") as fh:
            fh.write("# deny")

        with open(Path.joinpath(fn, "cloud/nonprod/badfile"), "w") as fh:
            fh.write("# blah")
        stuff = foldertest.squidcheck(fn)
        with pytest.raises(SystemExit):
            stuff.check()

        shutil.rmtree(fn)

    def test_squid_check_denylist(self, tmp_path_factory):
        fn = tmp_path_factory.mktemp("denycheck", numbered=False)
        with open(Path.joinpath(fn, "denylist"), "w") as fh:
            fh.write("# deny\nlake")
        stuff = foldertest.squidcheck(fn)
        with pytest.raises(ValueError, match="lake found in denylist file"):
            stuff.check_denylist("lake")

        shutil.rmtree(fn)

    def test_squid_checkdups(self, tmp_path_factory):
        fd = mock.Mock()
        fd.name = "nonprod"
        fn = tmp_path_factory.mktemp("dupcheck", numbered=False)
        for folder in ["prod", "nonprod"]:
            Path.mkdir(Path.joinpath(fn, f"cloud/{folder}"), parents=True)
            with open(
                Path.joinpath(fn, f"cloud/{folder}/domains-allowlist"), "w"
            ) as fh:
                fh.write(".domain.com # a domain\n.anotherdomain.com")
            with open(Path.joinpath(fn, f"cloud/{folder}/ips-allowlist"), "w") as fh:
                fh.write("192.168.0.0/24 # a prefix\n192.169.0.1 # a single ip")

        with open(Path.joinpath(fn, "denylist"), "w") as fh:
            fh.write("# deny")

        with open(Path.joinpath(fn, f"cloud/{fd.name}/domains-allowlist"), "a") as fh:
            fh.write("\n.domain.com # a domain\n.anotherdomain.com\n# a comment line\n")

        stuff = foldertest.squidcheck(fn)
        with pytest.raises(ValueError):
            stuff.checkdups(
                "cloud",
                Path.joinpath(fn, f"cloud/{fd.name}"),
                Path.joinpath(fn, f"cloud/{fd.name}/domains-allowlist"),
            )

        with open(Path.joinpath(fn, f"cloud/{folder}/ips-allowlist"), "a") as fh:
            fh.write("\n192.168.0.0/24 # a prefix\n192.169.0.1 # a single ip")
        with pytest.raises(ValueError):
            stuff.checkdups(
                "cloud",
                Path.joinpath(fn, f"cloud/{fd.name}"),
                Path.joinpath(fn, f"cloud/{fd.name}/ips-allowlist"),
            )

        shutil.rmtree(fn)

    def test_squid_checkdomaindata_ports(self, tmp_path_factory):
        fd = mock.Mock()
        fd.name = "nonprod"
        fn = tmp_path_factory.mktemp("dupcheck", numbered=False)
        for folder in ["prod", "nonprod"]:
            Path.mkdir(Path.joinpath(fn, f"cloud/{folder}"), parents=True)
            with open(
                Path.joinpath(fn, f"cloud/{folder}/domains-allowlist"), "w"
            ) as fh:
                fh.write(".domain.com # a domain\n.anotherdomain.com")
            with open(Path.joinpath(fn, f"cloud/{folder}/ips-allowlist"), "w") as fh:
                fh.write("192.168.0.0/24 # a prefix\n192.169.0.1 # a single ip")

        with open(Path.joinpath(fn, "denylist"), "w") as fh:
            fh.write("# deny")

        with open(Path.joinpath(fn, f"cloud/{fd.name}/domains-allowlist"), "a") as fh:
            fh.write("\n.domain.com:22 # a domain with port")

        stuff = foldertest.squidcheck(fn)
        with pytest.raises(
            ValueError,
            match="Port values found .domain.com:22 in cloud nonprod domains-allowlist",
        ):
            stuff.checkdomaindata(
                "cloud",
                Path.joinpath(fn, f"cloud/{fd.name}"),
                Path.joinpath(fn, f"cloud/{fd.name}/domains-allowlist"),
            )
        shutil.rmtree(fn)

    def test_squid_checkdomaindata_ips(self, tmp_path_factory):
        fd = mock.Mock()
        fd.name = "nonprod"
        fn = tmp_path_factory.mktemp("dupcheck", numbered=False)
        for folder in ["prod", "nonprod"]:
            Path.mkdir(Path.joinpath(fn, f"cloud/{folder}"), parents=True)
            with open(
                Path.joinpath(fn, f"cloud/{folder}/domains-allowlist"), "w"
            ) as fh:
                fh.write(".domain.com # a domain\n.anotherdomain.com")
            with open(Path.joinpath(fn, f"cloud/{folder}/ips-allowlist"), "w") as fh:
                fh.write("192.168.0.0/24 # a prefix\n192.169.0.1 # a single ip")

        with open(Path.joinpath(fn, "denylist"), "w") as fh:
            fh.write("# deny")

        with open(Path.joinpath(fn, f"cloud/{fd.name}/domains-allowlist"), "a") as fh:
            fh.write("\n192.168.0.1 # ip in domains file")

        stuff = foldertest.squidcheck(fn)
        with pytest.raises(
            ValueError,
            match="IP address/prefix record found 192.168.0.1 in cloud nonprod domains-allowlist",
        ):
            stuff.checkdomaindata(
                "cloud",
                Path.joinpath(fn, f"cloud/{fd.name}"),
                Path.joinpath(fn, f"cloud/{fd.name}/domains-allowlist"),
            )

        shutil.rmtree(fn)

    def test_squid_checkipdata_bad_prefix(self, tmp_path_factory):
        fd = mock.Mock()
        fd.name = "nonprod"
        fn = tmp_path_factory.mktemp("dupcheck", numbered=False)
        for folder in ["prod", "nonprod"]:
            Path.mkdir(Path.joinpath(fn, f"cloud/{folder}"), parents=True)
            with open(
                Path.joinpath(fn, f"cloud/{folder}/domains-allowlist"), "w"
            ) as fh:
                fh.write(".domain.com # a domain\n.anotherdomain.com")
            with open(Path.joinpath(fn, f"cloud/{folder}/ips-allowlist"), "w") as fh:
                fh.write("192.168.0.0/24 # a prefix\n192.169.0.1 # a single ip")

        with open(Path.joinpath(fn, "denylist"), "w") as fh:
            fh.write("# deny")

        with open(Path.joinpath(fn, f"cloud/{folder}/ips-allowlist"), "a") as fh:
            fh.write("\n192.168.0.2/24 # a prefix")

        stuff = foldertest.squidcheck(fn)

        with pytest.raises(
            ValueError,
            match="192.168.0.2/24 has host bits set",
        ):
            stuff.checkipdata(
                "cloud",
                Path.joinpath(fn, f"cloud/{fd.name}"),
                Path.joinpath(fn, f"cloud/{fd.name}/ips-allowlist"),
            )

        shutil.rmtree(fn)

    def test_squid_checkipdata_bad_range(self, tmp_path_factory):
        fd = mock.Mock()
        fd.name = "nonprod"
        fn = tmp_path_factory.mktemp("dupcheck", numbered=False)
        for folder in ["prod", "nonprod"]:
            Path.mkdir(Path.joinpath(fn, f"cloud/{folder}"), parents=True)
            with open(
                Path.joinpath(fn, f"cloud/{folder}/domains-allowlist"), "w"
            ) as fh:
                fh.write(".domain.com # a domain\n.anotherdomain.com")
            with open(Path.joinpath(fn, f"cloud/{folder}/ips-allowlist"), "w") as fh:
                fh.write("192.168.0.0/24 # a prefix\n192.169.0.1 # a single ip")

        with open(Path.joinpath(fn, "denylist"), "w") as fh:
            fh.write("# deny")

        with open(Path.joinpath(fn, f"cloud/{folder}/ips-allowlist"), "a") as fh:
            fh.write("\n10.0.0.1 # a blocked ip")

        stuff = foldertest.squidcheck(fn)

        with pytest.raises(
            ValueError,
            match="IP in private ranges record found 10.0.0.1 in cloud nonprod ips-allowlist",
        ):
            stuff.checkipdata(
                "cloud",
                Path.joinpath(fn, f"cloud/{fd.name}"),
                Path.joinpath(fn, f"cloud/{fd.name}/ips-allowlist"),
            )

        shutil.rmtree(fn)

    def test_squid_checkipdata_bad_ip(self, tmp_path_factory):
        fd = mock.Mock()
        fd.name = "nonprod"
        fn = tmp_path_factory.mktemp("dupcheck", numbered=False)
        for folder in ["prod", "nonprod"]:
            Path.mkdir(Path.joinpath(fn, f"cloud/{folder}"), parents=True)
            with open(
                Path.joinpath(fn, f"cloud/{folder}/domains-allowlist"), "w"
            ) as fh:
                fh.write(".domain.com # a domain\n.anotherdomain.com")
            with open(Path.joinpath(fn, f"cloud/{folder}/ips-allowlist"), "w") as fh:
                fh.write("192.168.0.0/24 # a prefix\n192.169.0.1 # a single ip")

        with open(Path.joinpath(fn, "denylist"), "w") as fh:
            fh.write("# deny")

        with open(Path.joinpath(fn, f"cloud/{folder}/ips-allowlist"), "a") as fh:
            fh.write("\n300.0.0.1 # a wtf ip")

        stuff = foldertest.squidcheck(fn)

        with pytest.raises(
            ValueError,
            match="'300.0.0.1' does not appear to be an IPv4 or IPv6 address",
        ):
            stuff.checkipdata(
                "cloud",
                Path.joinpath(fn, f"cloud/{fd.name}"),
                Path.joinpath(fn, f"cloud/{fd.name}/ips-allowlist"),
            )

        shutil.rmtree(fn)

    def test_squid_checkipdata_domainname(self, tmp_path_factory):
        fd = mock.Mock()
        fd.name = "nonprod"
        fn = tmp_path_factory.mktemp("dupcheck", numbered=False)
        for folder in ["prod", "nonprod"]:
            Path.mkdir(Path.joinpath(fn, f"cloud/{folder}"), parents=True)
            with open(
                Path.joinpath(fn, f"cloud/{folder}/domains-allowlist"), "w"
            ) as fh:
                fh.write(".domain.com # a domain\n.anotherdomain.com")
            with open(Path.joinpath(fn, f"cloud/{folder}/ips-allowlist"), "w") as fh:
                fh.write("192.168.0.0/24 # a prefix\n192.169.0.1 # a single ip")

        with open(Path.joinpath(fn, "denylist"), "w") as fh:
            fh.write("# deny")

        with open(Path.joinpath(fn, f"cloud/{folder}/ips-allowlist"), "a") as fh:
            fh.write("\ngoogle.com # a domain in the wrong file")

        stuff = foldertest.squidcheck(fn)

        with pytest.raises(
            ValueError,
            match="Not an IP google.com in cloud nonprod ips-allowlist",
        ):
            stuff.checkipdata(
                "cloud",
                Path.joinpath(fn, f"cloud/{fd.name}"),
                Path.joinpath(fn, f"cloud/{fd.name}/ips-allowlist"),
            )

        shutil.rmtree(fn)

    def test_squid_uncomment(self, tmp_path_factory):
        d = foldertest.squidcheck.uncomment("blah")
        assert d == "blah"

        d = foldertest.squidcheck.uncomment("blah # stuff")
        assert d == "blah"

        d = foldertest.squidcheck.uncomment("# stuff")
        assert d is None

        # Strips whitespace
        d = foldertest.squidcheck.uncomment("10.0.0.0     # stuff")
        assert d == "10.0.0.0"

        # Strips whitespace
        d = foldertest.squidcheck.uncomment("10.0.0.0     ")
        assert d == "10.0.0.0"

        # Strips whitespace
        d = foldertest.squidcheck.uncomment("      10.0.0.0     ")
        assert d == "10.0.0.0"
