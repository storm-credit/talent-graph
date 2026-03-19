"""Tests for CSV import."""

from talentgraph.estimation.csv_import import parse_csv


class TestCsvImport:
    def test_basic_csv(self):
        csv = "name,position,department,hire_date\n김철수,과장,영업부,2020-03-15\n이영희,사원,개발부,2023-01-01"
        result = parse_csv(csv)
        assert result.imported_count == 2
        assert result.imported[0].name == "김철수"
        assert result.imported[0].position == "과장"
        assert result.imported[1].department == "개발부"

    def test_korean_headers(self):
        csv = "이름,직급,부서,입사일\n박지민,대리,마케팅,2021-06-01"
        result = parse_csv(csv)
        assert result.imported_count == 1
        assert result.imported[0].name == "박지민"

    def test_missing_name_error(self):
        csv = "name,position,department,hire_date\n,과장,영업부,2020-01-01"
        result = parse_csv(csv)
        assert result.imported_count == 0
        assert len(result.errors) == 1

    def test_missing_position_warning(self):
        csv = "name,position,department,hire_date\n김철수,,영업부,2020-01-01"
        result = parse_csv(csv)
        assert result.imported_count == 1
        assert result.imported[0].position == "사원"
        assert len(result.warnings) == 1

    def test_empty_csv(self):
        csv = ""
        result = parse_csv(csv)
        assert result.imported_count == 0
        assert len(result.errors) > 0

    def test_various_date_formats(self):
        csv = "name,position,department,hire_date\nA,사원,개발,2020/03/15\nB,대리,영업,2020.06.01"
        result = parse_csv(csv)
        assert result.imported_count == 2

    def test_unknown_headers(self):
        csv = "foo,bar,baz,qux\n1,2,3,4"
        result = parse_csv(csv)
        assert result.imported_count == 0
        assert len(result.errors) > 0
