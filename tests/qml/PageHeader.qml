import QtQuick
import QtQuick.Layouts

// Back button + small accent caption + big title + divider line.
ColumnLayout {
    id: header

    property string eyebrow: ""
    property string title: ""
    property string backText: "Home"

    signal backClicked()

    spacing: 18

    RowLayout {
        Layout.fillWidth: true

        SharpButton {
            text: "←  " + header.backText
            onClicked: header.backClicked()
        }
        Item { Layout.fillWidth: true }
    }

    ColumnLayout {
        spacing: 4

        SectionLabel {
            text: header.eyebrow
            color: theme.accent
        }
        Text {
            text: header.title
            color: theme.text
            font.pixelSize: 38
            font.weight: Font.Bold
            font.capitalization: Font.AllUppercase
        }
    }

    Rectangle {
        Layout.fillWidth: true
        Layout.preferredHeight: 1
        color: theme.border
    }
}
