import sys
from tkinter import filedialog, messagebox

import pytest
import ttkbootstrap as tb
from PIL import Image
from pypdf import PdfReader

from rss_islandr.core.datatypes import UICalcVariable, UIInpVariable
from rss_islandr.ui.io_btns import ExportPDFReportBtn, IOBtns

POLYGONS = (
    "[{'unique_id': 'a', 'type': 'polygon', 'name': 'P1', "
    "'coordinates': [[38.0, 54.5], [38.1, 54.6], [38.2, 54.5]], 'area_km2': 1.2, 'node_count': 3}]"
)


def _inp_var(frame_tag, value, text_val, table):
    return UIInpVariable(
        frame_tag=frame_tag,
        tk_var=tb.StringVar(value=value),
        rel_pos=0,
        text_val=text_val,
        pdf_table_name=table,
    )


@pytest.fixture
def export(root, tmp_path, monkeypatch):
    """Run the PDF export with prefilled variables. Returns a function that runs it and returns (file, errors)."""
    ui_inp_vars = {
        "val_0_00": _inp_var("site_info_frame", "Test site", "Site name", "Site information"),
        "map_0_01": _inp_var("site_info_frame", "54.5733123", "Latitude", "Site information"),
        "drop_on-on_IN_1_00": _inp_var("IN_on-on_frame", "Toxic metals", "Toxicity", "Source hazard"),
        "drop_on-off_IN_1_00": _inp_var("IN_on-off_frame", "Small", "Extent", "Source hazard"),
        "drop_off-on_IN_1_00": _inp_var("IN_off-on_frame", "Large", "Extent", "Source hazard"),
    }
    ui_calc_vars = {"IN_on-on_frame": UICalcVariable(tb.StringVar(value="0.35"), "C9")}
    errors = []
    monkeypatch.setattr(messagebox, "showinfo", lambda *args, **kwargs: None)
    monkeypatch.setattr(messagebox, "showerror", lambda *args, **kwargs: errors.append(args))

    def run(image_files=(), polygons="", target=None, variables=None):
        target = tmp_path / "report.pdf" if target is None else target
        monkeypatch.setattr(messagebox, "askyesno", lambda *args, **kwargs: bool(image_files))
        monkeypatch.setattr(filedialog, "askopenfilenames", lambda **kwargs: [str(f) for f in image_files])
        monkeypatch.setattr(filedialog, "asksaveasfilename", lambda **kwargs: str(target))
        button = ExportPDFReportBtn(
            variables or ui_inp_vars, ui_calc_vars, map_polygons_tb=tb.StringVar(value=polygons)
        )
        button.on_btn_click()
        return target, errors

    run.inp_vars = ui_inp_vars
    return run


def _text(pdf_file):
    return "\n".join(page.extract_text() for page in PdfReader(pdf_file).pages)


def test_report_has_title_contents_sections_and_tables(export):
    """
    Steps:
    1. Prepare the site information, the source of two scenarios and one calculated risk (0.35).
    2. Export the PDF report without map images and polygons.

    Expected result:
    - The PDF has a title page, a table of contents and a section for the site information and for each scenario.
    - The tables list the selected values and the risk is shown in percent (35.00).
    - There is no page for figures or polygons.
    """
    target, errors = export()

    assert errors == []
    text = _text(target)
    for expected in (
        "Contamination Analysis Report",
        "Contents",
        "Site information",
        "On-site to on-site contamination",
        "On-site to off-site contamination",
        "Off-site to on-site contamination",
        "Test site",
        "Toxic metals",
        "Calculated Risk [%]",
        "35.00",
    ):
        assert expected in text
    assert "Figures" not in text
    assert "Polygon Data" not in text


def test_latitude_is_rounded_to_four_decimals(export):
    """
    Steps:
    1. Enter the latitude 54.5733123.
    2. Export the PDF report.

    Expected result:
    - The report shows the latitude as 54.5733.
    """
    target, _ = export()

    text = _text(target)
    assert "54.5733" in text
    assert "54.5733123" not in text


def test_latitude_that_is_not_a_number_is_left_empty(export):
    """
    Steps:
    1. Enter the text "abc" as the latitude.
    2. Export the PDF report.

    Expected result:
    - The report is created without an error and does not contain "abc".
    """
    export.inp_vars["map_0_01"].tk_var.set("abc")

    target, errors = export()

    assert errors == []
    assert "abc" not in _text(target)


def test_report_has_figures_and_polygon_table(export, tmp_path):
    """
    Steps:
    1. Create a PNG map image.
    2. Export the PDF report with the image and one polygon (three nodes, area 1.2 km2).

    Expected result:
    - A "Figures" page contains the image.
    - A "Polygon Data" page has the polygon name, the coordinates of the nodes, the area and the number of nodes.
    """
    image_file = tmp_path / "map.png"
    Image.new("RGB", (400, 300), (70, 130, 180)).save(image_file)

    target, errors = export([image_file], POLYGONS)

    assert errors == []
    reader = PdfReader(target)
    figures_page = next(page for page in reader.pages if page.extract_text().startswith("Figures"))
    assert len(figures_page.images) == 1
    text = _text(target)
    for expected in ("Polygon Data", "P1", "38.100000", "54.600000", "1.20"):
        assert expected in text


def test_report_is_a_pdf_file_with_the_expected_pages(export):
    """
    Steps:
    1. Export the PDF report.
    2. Open the file with a PDF reader.

    Expected result:
    - The file is a PDF with 6 pages: title, contents, site information and the three scenarios.
    """
    target, _ = export()

    assert target.read_bytes().startswith(b"%PDF")
    assert len(PdfReader(target).pages) == 6


def test_error_is_reported_when_the_report_cannot_be_written(export, tmp_path):
    """
    Steps:
    1. Export the PDF report to a file in a folder that does not exist.

    Expected result:
    - No file is created and one error message is shown.
    """
    target, errors = export(target=tmp_path / "missing_folder" / "report.pdf")

    assert not target.exists()
    assert len(errors) == 1 and errors[0][0] == "Error"


def test_variable_of_an_unknown_page_is_reported(export):
    """
    Steps:
    1. Add a variable that belongs to no known page (frame tag "unknown_frame").
    2. Export the PDF report.

    Expected result:
    - An error message names the unknown page.
    """
    variables = dict(export.inp_vars)
    variables["other"] = _inp_var("unknown_frame", "x", "Other", "Other table")

    _, errors = export(variables=variables)

    assert len(errors) == 1
    assert "unknown_frame" in errors[0][1]


def test_cancelled_dialog_creates_no_report(export, tmp_path):
    """
    Steps:
    1. Export the PDF report and cancel the file dialog (empty file name).

    Expected result:
    - No file is written and no message is shown.
    """
    target, errors = export(target="")

    assert errors == []
    assert list(tmp_path.iterdir()) == []


def test_map_images_are_offered_only_on_request(monkeypatch):
    """
    Steps:
    1. Ask for map images and answer "No".
    2. Ask again, answer "Yes" and select two files.

    Expected result:
    - The first time the result is an empty list and the user is informed.
    - The second time the list has the two selected files.
    """
    infos = []
    monkeypatch.setattr(messagebox, "showinfo", lambda *args, **kwargs: infos.append(args))
    monkeypatch.setattr(messagebox, "askyesno", lambda *args, **kwargs: False)
    assert IOBtns.add_maps_prompt("pdf") == []
    assert len(infos) == 1

    monkeypatch.setattr(messagebox, "askyesno", lambda *args, **kwargs: True)
    monkeypatch.setattr(filedialog, "askopenfilenames", lambda **kwargs: ("a.png", "b.png"))
    assert IOBtns.add_maps_prompt("pdf") == ["a.png", "b.png"]


if __name__ == "__main__":
    # Enforce executing only this file verbose option and print statements in functions to be printed
    pytest.main([sys.argv[0], "-v", "-s"])
