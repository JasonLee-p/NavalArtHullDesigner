import os
import shutil
import sys
import traceback
import webbrowser

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from PyQt5.QtCore import QEvent, QPoint, Qt
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox


def main():
    src = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join("sample_projects", "sample.naprj"))
    tmp = os.path.abspath(".pytest-ui-sample.naprj")
    shutil.copyfile(src, tmp)

    QMessageBox.warning = lambda *args, **kwargs: QMessageBox.Ok
    QMessageBox.information = lambda *args, **kwargs: QMessageBox.Ok
    QFileDialog.exec = lambda self: 0
    QFileDialog.exec_ = lambda self: 0
    webbrowser.open = lambda *args, **kwargs: True

    app = QApplication(sys.argv)

    from GUI.main_widgets import GLWidgetGUI
    from main_editor import MainEditor
    from main_logger import Log

    editor = MainEditor(GLWidgetGUI(), Log())
    assert editor.open_prj(tmp)
    editor.show()
    app.processEvents()

    failures = []

    def run(name, func):
        try:
            func()
            app.processEvents()
            print(f"PASS {name}", flush=True)
        except Exception:
            failures.append((name, traceback.format_exc()))
            print(f"FAIL {name}", flush=True)

    def mouse_left(widget):
        event = QMouseEvent(QEvent.MouseButtonPress, QPoint(5, 5), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
        widget.mousePressEvent(event)

    def nudge_number(edit, delta=0.1):
        if not edit.isEnabled():
            return
        edit.setText(str(edit.current_value + delta))
        edit.valueSetted()

    def exercise_current_editor(prefix):
        widget = editor.edit_tab.current_edit_widget
        if widget is None:
            return
        run(f"{prefix} edit posX", lambda widget=widget: nudge_number(widget.posX_edit))
        run(f"{prefix} edit posY", lambda widget=widget: nudge_number(widget.posY_edit))
        run(f"{prefix} edit posZ", lambda widget=widget: nudge_number(widget.posZ_edit))
        run(f"{prefix} edit rotX", lambda widget=widget: nudge_number(widget.rotX_edit))
        run(f"{prefix} edit rotY", lambda widget=widget: nudge_number(widget.rotY_edit))
        run(f"{prefix} edit rotZ", lambda widget=widget: nudge_number(widget.rotZ_edit))

    containers = [
        ("hull", editor.structure_tab.hullSectionGroup_tab),
        ("armor", editor.structure_tab.armorSectionGroup_tab),
        ("bridge", editor.structure_tab.bridge_tab),
        ("ladder", editor.structure_tab.ladder_tab),
        ("model", editor.structure_tab.model_tab),
        ("ref_image", editor.structure_tab.refImage_tab),
    ]
    for container_name, container in containers:
        for index, item in enumerate(list(container._items)):
            run(f"{container_name}[{index}] select", lambda item=item: mouse_left(item._showButton))
            run(f"{container_name}[{index}] visibility", lambda item=item: item._showButton.vis_btn.click())
            run(f"{container_name}[{index}] direct editor", lambda item=item: editor.show_editor([item]))
            exercise_current_editor(f"{container_name}[{index}]")

    for index, group in enumerate(list(editor.structure_tab.hullSectionGroup_tab._items)):
        run(f"hull[{index}] editor open", lambda group=group: editor.show_editor([group]))
        for section_index, section in enumerate(group.get_sections()):
            run(
                f"hull[{index}].section[{section_index}] select",
                lambda section=section: mouse_left(section.showButton()),
            )
            run(
                f"hull[{index}].section[{section_index}] visibility",
                lambda section=section: section.showButton().vis_btn.click(),
            )
            run(
                f"hull[{index}].section[{section_index}] edit z",
                lambda section=section: nudge_number(section.showButton().posZ_edit),
            )

    run("tools move dialog open", editor.tools_tab.moveButton.click)
    run("tools scale dialog open", editor.tools_tab.scaleButton.click)

    for menu_button in editor.menuButtons:
        menu = menu_button.menu()
        if menu is None:
            continue
        for action in menu.actions():
            action_name = action.text()
            if action_name.startswith("保存") or action_name.startswith("另存") or action_name.startswith("导出"):
                continue
            run(f"menu {menu_button.text()}/{action_name}", lambda action=action: action.trigger())

    if failures:
        print("\nFAILURES", flush=True)
        for name, trace in failures:
            print(f"\n--- {name} ---\n{trace}", flush=True)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
