import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: page

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 48
        spacing: 22

        PageHeader {
            Layout.fillWidth: true
            eyebrow: "02 / Directory"
            title: "All members"
            onBackClicked: page.StackView.view.pop()
        }

        SectionLabel {
            text: backend.members.length + (backend.members.length === 1 ? " member" : " members")
        }

        // column captions
        RowLayout {
            Layout.fillWidth: true
            Layout.leftMargin: 21
            Layout.rightMargin: 13
            spacing: 20

            SectionLabel { text: "ID"; Layout.preferredWidth: 72 }
            SectionLabel { text: "Full name"; Layout.fillWidth: true }
            Item { Layout.preferredWidth: 170 }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: theme.surface
            border.width: 1
            border.color: theme.border

            ListView {
                id: list
                anchors.fill: parent
                anchors.margins: 1
                clip: true
                boundsBehavior: Flickable.StopAtBounds
                model: backend.members

                ScrollBar.vertical: ScrollBar {
                    id: bar
                    policy: ScrollBar.AsNeeded
                    contentItem: Rectangle {
                        implicitWidth: 6
                        color: bar.pressed ? theme.accent : theme.scroll
                    }
                    background: Rectangle { color: "transparent" }
                }

                delegate: Rectangle {
                    id: row
                    required property var modelData

                    width: ListView.view.width
                    height: 64
                    color: rowHover.hovered ? theme.surfaceHi : "transparent"

                    HoverHandler { id: rowHover }

                    // accent bar on the left when hovered
                    Rectangle {
                        width: 3
                        height: parent.height
                        color: theme.accent
                        visible: rowHover.hovered
                    }
                    // row separator
                    Rectangle {
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.bottom: parent.bottom
                        height: 1
                        color: theme.border
                    }

                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: 20
                        anchors.rightMargin: 12
                        spacing: 20

                        Text {
                            Layout.preferredWidth: 72
                            text: "#" + row.modelData.id
                            color: theme.accent
                            font.pixelSize: 16
                            font.weight: Font.Bold
                        }
                        Text {
                            Layout.fillWidth: true
                            text: row.modelData.fullName
                            color: theme.text
                            font.pixelSize: 17
                            elide: Text.ElideRight
                        }
                        SharpButton {
                            Layout.preferredWidth: 170
                            text: "Member info"
                            onClicked: page.StackView.view.push(
                                "MemberInfoPage.qml", { memberId: row.modelData.id })
                        }
                    }
                }
            }

            Text {
                anchors.centerIn: parent
                visible: list.count === 0
                text: "No members yet. Add one from the home page."
                color: theme.muted
                font.pixelSize: 15
            }
        }
    }
}
