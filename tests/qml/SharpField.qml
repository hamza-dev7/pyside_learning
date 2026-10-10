import QtQuick
import QtQuick.Controls

// Square text box. Border and a left bar light up in the accent colour on focus.
TextField {
    id: control

    hoverEnabled: true
    selectByMouse: true
    implicitHeight: 48
    leftPadding: 18
    rightPadding: 16
    font.pixelSize: 15
    color: theme.text
    placeholderTextColor: theme.muted
    selectionColor: theme.accent
    selectedTextColor: theme.onAccent
    verticalAlignment: TextInput.AlignVCenter

    background: Rectangle {
        radius: 0
        color: theme.surface
        border.width: 1
        border.color: control.activeFocus ? theme.accent
                    : control.hovered ? theme.borderHi
                    : theme.border

        Behavior on border.color { ColorAnimation { duration: 110 } }

        Rectangle {
            width: 3
            height: parent.height
            color: theme.accent
            visible: control.activeFocus
        }
    }
}
