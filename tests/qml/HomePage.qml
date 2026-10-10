import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: page

    RowLayout {
        anchors.fill: parent
        anchors.margins: 56
        spacing: 64

        // ---- left: brand block ------------------------------------------
        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.preferredWidth: 1
            spacing: 4

            Item { Layout.fillHeight: true }

            Rectangle {
                Layout.preferredWidth: 64
                Layout.preferredHeight: 10
                color: theme.accent
            }
            Item { Layout.preferredHeight: 16 }

            Text {
                Layout.fillWidth: true
                text: "GYM"
                color: theme.text
                font.pixelSize: 88
                font.weight: Font.Bold
                fontSizeMode: Text.HorizontalFit
                minimumPixelSize: 36
            }
            Text {
                Layout.fillWidth: true
                text: "MANAGER"
                color: theme.accent
                font.pixelSize: 88
                font.weight: Font.Bold
                fontSizeMode: Text.HorizontalFit
                minimumPixelSize: 36
            }

            Item { Layout.preferredHeight: 16 }
            Text {
                Layout.fillWidth: true
                text: "Members and memberships, under control."
                color: theme.muted
                font.pixelSize: 16
                wrapMode: Text.WordWrap
            }

            Item { Layout.fillHeight: true }
        }

        // ---- right: the three options -----------------------------------
        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.preferredWidth: 1
            spacing: 12

            Item { Layout.fillHeight: true }

            SectionLabel { text: "Menu" }

            ActionTile {
                Layout.fillWidth: true
                number: "01"
                label: "Add a member"
                caption: "Register a new member"
                onClicked: page.StackView.view.push("AddMemberPage.qml")
            }
            ActionTile {
                Layout.fillWidth: true
                number: "02"
                label: "All members"
                caption: "Browse and manage memberships"
                onClicked: page.StackView.view.push("MembersPage.qml")
            }
            ActionTile {
                Layout.fillWidth: true
                number: "03"
                label: "Find by ID"
                caption: "Jump straight to a member"
                onClicked: page.StackView.view.push("SearchPage.qml")
            }

            Item { Layout.fillHeight: true }
        }
    }
}
