import QtQuick
import QtQuick.Controls

// Flat, square-cornered button.
//   default  -> outlined
//   primary  -> solid accent colour
//   danger   -> red outline, fills red on hover
Button {
    id: control

    property bool primary: false
    property bool danger: false

    hoverEnabled: true
    implicitHeight: 46
    leftPadding: 22
    rightPadding: 22
    opacity: enabled ? 1.0 : 0.35

    readonly property color fillColor: {
        if (primary)
            return down ? theme.accentPress : (hovered ? theme.accentHover : theme.accent)
        if (danger)
            return down ? theme.dangerPress : (hovered ? theme.danger : "transparent")
        return hovered || down ? theme.surfaceHi : "transparent"
    }
    readonly property color lineColor: primary ? fillColor
                                     : danger ? theme.danger
                                     : (hovered ? theme.borderHi : theme.border)
    readonly property color labelColor: primary ? theme.onAccent
                                      : danger ? (hovered ? "#ffffff" : theme.danger)
                                      : theme.text

    contentItem: Text {
        text: control.text
        color: control.labelColor
        font.pixelSize: 12
        font.weight: Font.DemiBold
        font.letterSpacing: 1.4
        font.capitalization: Font.AllUppercase
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        elide: Text.ElideRight
    }

    background: Rectangle {
        radius: 0
        color: control.fillColor
        border.width: 1
        border.color: control.lineColor

        Behavior on color { ColorAnimation { duration: 110 } }
    }

    // Only changes the mouse cursor; lets clicks pass through to the button.
    MouseArea {
        anchors.fill: parent
        acceptedButtons: Qt.NoButton
        cursorShape: control.enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
    }
}
