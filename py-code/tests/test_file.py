from py_code.io.file.base_file import BaseFile
from py_code.io.file.file import File
from tempfile import TemporaryDirectory

class TestFile:

    def test_import_export(self, file: BaseFile):
        """Test file import/export doesn't alter asset plaintext"""
        import_plnm = file.plnm.__copy__()

        with TemporaryDirectory() as tmp_dir:
            export_filepath = file.save(export_dir=tmp_dir)
            export_file = File(export_filepath)
            assert import_plnm == export_file.plnm
