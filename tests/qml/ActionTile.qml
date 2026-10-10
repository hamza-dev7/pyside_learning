import QtQuick
import QtQuick.Layouts

// Big menu row on the home page. Floods with the accent colour on hover.
Rectangle {
    id: tile

    property string number: ""
    property string label: ""
    property string caption: ""
    readonly property bool hot: mouse.containsMouse

    signal clicked()

    implicitHeight: 104
    color: hot ? theme.accent : theme.surface
    border.width: 1
    border.color: hot ? theme.accent : theme.border

    Behavior on color { ColorAnimation { duration: 140 } }

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 26
        anchors.rightMargin: 26
        spacing: 26

        Text {
            text: tile.number
            color: tile.hot ? theme.onAccent : theme.accent
            font.pixelSize: 16
            font.weight: Font.Bold
            font.letterSpacing: 2
        }

        ColumnLayout {
            Layout.fillWidth: true
            spacing: 2

            Text {
                text: tile.label
                color: tile.hot ? theme.onAccent : theme.text
                font.pixelSize: 24
                font.weight: Font.Bold
                font.capitalization: Font.AllUppercase
                font.letterSpacing: 1
            }
            Text {
                text: tile.caption
                color: tile.hot ? theme.onAccent : theme.muted
                font.pixelSize: 13
            }
        }

        Text {
            text: "→"
            color: tile.hot ? theme.onAccent : theme.text
            font.pixelSize: 30
        }
    }

    MouseArea {
        id: mouse
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: tile.clicked()
    }
}
