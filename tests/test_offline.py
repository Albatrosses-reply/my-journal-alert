"""오프라인 테스트: 네트워크 없이 파싱·제외 규칙·병합·키워드·렌더링·설정 마법사·초록 보충을 검증한다."""
import os
import sys
import tempfile
import tomllib
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import setup  # noqa: E402
from alert import abstracts, config, render  # noqa: E402
from alert.collect import Collector, Paper, excluded, rebuild_abstract, score  # noqa: E402

J = {"abbrev": "JUE", "name": "Journal of Urban Economics", "issn": ["0094-1190"], "group": "realestate_core"}


class FakeHttp:
    def __init__(self, answers):
        self.answers, self.calls = answers, []

    def get_json(self, url, params=None, headers=None):
        self.calls.append(url)
        return next((v for k, v in self.answers.items() if k in url), None)

    def request(self, url, params=None, body=None, headers=None):
        self.calls.append(url)
        return self.answers.get("batch")


class CollectTests(unittest.TestCase):
    def test_exclude(self):
        for t in ("Resolution Design and Investment in Banking Groups – CORRIGENDUM", "Frontmatter of Econometrica 94 Iss. 3",
                  "The Econometric Society Annual Reports Report of the Treasurer", "2025 Election of Fellows to the Econometric Society",
                  "Correction to: Housing supply", "Issue Information", ""):
            self.assertTrue(excluded(t), t)
        for t in ("Corrections in house prices after zoning reform", "The decline of branch banking"):
            self.assertFalse(excluded(t), t)

    def test_parse_and_merge(self):
        cr = {"DOI": "10.1016/J.JUE.2026.1", "title": ["<i>Zoning</i> and rents"], "author": [{"given": "Ann", "family": "Lee"}],
              "published-online": {"date-parts": [[2026, 10, 2]]}}
        oa = {"doi": "https://doi.org/10.1016/j.jue.2026.1", "title": "Zoning and rents", "type": "article",
              "authorships": [{"author": {"display_name": "Ann Lee"}}], "publication_date": "2026-10-01",
              "abstract_inverted_index": {"We": [0], "study": [1], "zoning": [2]}}
        c = Collector(http=FakeHttp({}))
        a, b = c.from_crossref(cr, J), c.from_openalex(oa, J)
        self.assertEqual((a.doi, a.title, a.pub_date, a.abstract), ("10.1016/j.jue.2026.1", "Zoning and rents", "2026-10-02", ""))
        self.assertEqual((b.abstract, b.abstract_src), ("We study zoning", "OpenAlex"))
        c.crossref = lambda j, since: [a]
        c.openalex = lambda j, since: [b]
        (m,) = c.collect(J, date(2026, 10, 1))
        self.assertEqual((m.abstract, m.abstract_src, m.sources), ("We study zoning", "OpenAlex", {"crossref", "openalex"}))
        self.assertEqual(rebuild_abstract(None), "")

    def test_keywords(self):
        p = Paper(doi="x", title="Rental housing and mortgages", abstract="")
        self.assertEqual(score(p, ["housing", "rent*", "mortgage", "zoning"]), 3)
        self.assertEqual(score(Paper(doi="y", title="Parental leave"), ["rent*"]), 0)  # 단어 중간은 안 맞음


class RenderTests(unittest.TestCase):
    def test_chunks_and_labels(self):
        ps = [Paper(doi=f"10.1/{i}", title=f"Paper {i}", authors=["A", "B", "C", "D", "E"], journal="Cities", abbrev="Cities",
                    group="realestate_ext", pub_date="2026-10-01", abstract="x" * 3000, abstract_src="Elsevier", score=i % 2)
              for i in range(40)]
        chunks = render.body_chunks("2026-10-07", ps, [("realestate_ext", "부동산 확장")], "student")
        self.assertTrue(chunks[0].startswith("@student"))
        self.assertIn("초록 (Elsevier)", chunks[0])
        self.assertIn("A, B, C 외 2명", chunks[0])
        self.assertEqual(render.title("2026-10-07", ps), "📚 논문 알림 2026-10-07 · 40편 (⭐ 20)")
        many = [Paper(doi=f"10.2/{i}", title="T", journal=f"J{i}", abbrev=f"J{i}", group="g", abstract="y" * 3000) for i in range(40)]
        parts = render.body_chunks("d", many, [("g", "G")])
        self.assertGreater(len(parts), 1)
        self.assertTrue(all(len(c) <= render.LIMIT + 5000 for c in parts))


class SetupTests(unittest.TestCase):
    def test_write_and_load(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "journals.toml").write_text((ROOT / "journals.toml").read_text(encoding="utf-8"), encoding="utf-8")
            saved = setup.ROOT
            setup.ROOT = root
            try:
                setup.write_config(["realestate_core", "finance"], ['rent*', 'say "hi"'], ["finance"],
                                   [{"abbrev": "JRS", "name": "Journal of Regional Science", "issn": ["0022-4146"]}])
            finally:
                setup.ROOT = saved
            cfg = config.load(root)
            self.assertEqual(cfg["keywords"], ["rent*", 'say "hi"'])
            js = config.journals(cfg)
            self.assertEqual(js[-1]["group"], "extra")
            self.assertIn("JF", [j["abbrev"] for j in js])
            self.assertEqual(config.group_order(cfg)[-1], ("extra", "추가 저널"))

    def test_resolve(self):
        http = FakeHttp({"journals/0022-4146": {"message": {"title": "Journal of Regional Science", "ISSN": ["0022-4146", "1467-9787"]}},
                         "journals": {"message": {"items": [{"title": "Housing Studies Review", "ISSN": ["1111-1111"]},
                                                            {"title": "Housing Studies", "ISSN": ["0267-3037"]}]}}})
        self.assertEqual(setup.resolve("00224146", http)["issn"], ["0022-4146", "1467-9787"])
        self.assertEqual(setup.resolve("housing studies", http)["name"], "Housing Studies")
        self.assertEqual(setup.abbrev_of("Journal of Regional Science"), "JRS")

    def test_main_groups(self):
        env = {"REALESTATE": "핵심만", "ECONOMICS": "true", "FINANCE": "false", "MANAGEMENT": "false",
               "KEYWORD_FILTER": "true", "KEYWORDS": "housing, rent*", "EXTRA_JOURNALS": ""}
        with tempfile.TemporaryDirectory() as tmp:
            saved_root, saved_env = setup.ROOT, dict(os.environ)
            setup.ROOT = Path(tmp)
            os.environ.update(env)
            os.environ.pop("GITHUB_STEP_SUMMARY", None)
            try:
                self.assertEqual(setup.main(), 0)
                cfg = tomllib.loads((Path(tmp) / "alert.toml").read_text(encoding="utf-8"))
            finally:
                setup.ROOT = saved_root
                os.environ.clear()
                os.environ.update(saved_env)
        self.assertEqual((cfg["groups"], cfg["keyword_only_groups"]), (["realestate_core", "economics"], ["economics"]))


class AbstractTests(unittest.TestCase):
    def test_elsevier_and_s2(self):
        ps = [Paper(doi="10.1016/j.jue.2026.1", title="a"), Paper(doi="10.1080/x", title="b"), Paper(doi="10.1111/y", title="c", abstract="have")]
        http = FakeHttp({"api.elsevier.com": {"full-text-retrieval-response": {"coredata": {"dc:description": " Abstract We study. "}}},
                         "batch": [{"abstract": "From S2."}]})
        self.assertEqual(abstracts.elsevier(ps, http, "k"), 1)
        self.assertEqual(abstracts.semantic_scholar(ps, http), 1)
        self.assertEqual([(p.abstract, p.abstract_src) for p in ps[:2]], [("We study.", "Elsevier"), ("From S2.", "Semantic Scholar")])


if __name__ == "__main__":
    unittest.main()
