import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

// Shows one member and everything you can do to them.
// Used by both MemberInfoPage and SearchPage.
Rectangle {
    id: panel

    property int memberId: -1
    property var member: ({})                       // dict from backend.getMember()
    readonly property bool hasPlan: member.hasPlan === true

    signal memberDeleted(int deletedId)

    implicitWidth: 640
    implicitHeight: content.implicitHeight + 56
    color: theme.surface
    border.width: 1
    border.color: theme.border

    function reload() {
        member = backend.getMember(memberId)
    }
    onMemberIdChanged: reload()
    Component.onCompleted: reload()

    // any change in the backend -> re-read this member
    Connections {
        target: backend
        function onUpdated() { panel.reload() }
    }

    // accent bar down the left edge
    Rectangle {
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        width: 4
        color: theme.accent
    }

    ColumnLayout {
        id: content
        anchors.fill: parent
        anchors.topMargin: 28
        anchors.bottomMargin: 28
        anchors.leftMargin: 36
        anchors.rightMargin: 28
        spacing: 22

        // ---- who ----------------------------------------------------------
        RowLayout {
            Layout.fillWidth: true
            spacing: 24

            ColumnLayout {
                spacing: 0
                SectionLabel { text: "Member ID" }
                Text {
                    text: "#" + (panel.member.id !== undefined ? panel.member.id : "")
                    color: theme.accent
                    font.pixelSize: 44
                    font.weight: Font.Bold
                }
            }

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 4
                Text {
                    Layout.fillWidth: true
                    text: panel.member.fullName || ""
                    color: theme.text
                    font.pixelSize: 30
                    font.weight: Font.Bold
                    elide: Text.ElideRight
                }
                Text {
                    text: panel.member.phone || "No phone on file"
                    color: theme.muted
                    font.pixelSize: 14
                }
            }
        }

        Rectangle { Layout.fillWidth: true; Layout.preferredHeight: 1; color: theme.border }

        // ---- membership ----------------------------------------------------
        RowLayout {
            Layout.fillWidth: true

            SectionLabel { text: "Membership" }
            Item { Layout.fillWidth: true }

            // status chip: ACTIVE (accent) / EXPIRED (red) / NO MEMBERSHIP (grey)
            Rectangle {
                id: chip
                readonly property color tone: panel.member.status === "active" ? theme.accent
                                            : panel.member.status === "expired" ? theme.danger
                                            : theme.muted
                implicitWidth: chipText.implicitWidth + 24
                implicitHeight: 28
                color: "transparent"
                border.width: 1
                border.color: tone

                Text {
                    id: chipText
                    anchors.centerIn: parent
                    text: panel.member.statusText || ""
                    color: chip.tone
                    font.pixelSize: 11
                    font.weight: Font.DemiBold
                    font.letterSpacing: 1.5
                    font.capitalization: Font.AllUppercase
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 16

            Repeater {
                model: [
                    { caption: "Plan",    value: panel.hasPlan ? panel.member.planLabel : "—" },
                    { caption: "Started", value: panel.hasPlan ? panel.member.startDate : "—" },
                    { caption: "Expires", value: panel.hasPlan ? panel.member.endDate : "—" }
                ]

                delegate: ColumnLayout {
                    required property var modelData
                    Layout.fillWidth: true
                    Layout.preferredWidth: 1
                    spacing: 4

                    SectionLabel { text: modelData.caption }
                    Text {
                        text: modelData.value
                        color: theme.text
                        font.pixelSize: 20
                        font.weight: Font.DemiBold
                    }
                }
            }
        }

        // ---- membership actions -----------------------------------------------
        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            SharpButton {
                Layout.fillWidth: true
                Layout.preferredWidth: 1
                text: "Add membership"
                primary: true
                enabled: !panel.hasPlan && panel.member.id !== undefined
                onClicked: planDialog.openFor("Add membership", 0)
            }
            SharpButton {
                Layout.fillWidth: true
                Layout.preferredWidth: 1
                text: "Change membership"
                enabled: panel.hasPlan
                onClicked: planDialog.openFor("Change membership", panel.member.planMonths)
            }
            SharpButton {
                Layout.fillWidth: true
                Layout.preferredWidth: 1
                text: "Cancel membership"
                enabled: panel.hasPlan
                onClicked: confirmDialog.ask(
                    "cancel",
                    "Cancel membership",
                    "End " + (panel.member.fullName || "this member") + "'s "
                        + (panel.member.planLabel || "") + " membership?",
                    "Cancel it")
            }
        }

        Rectangle { Layout.fillWidth: true; Layout.preferredHeight: 1; color: theme.border }

        // ---- danger zone -----------------------------------------------------
        RowLayout {
            Layout.fillWidth: true
            spacing: 20

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 4
                SectionLabel { text: "Danger zone" }
                Text {
                    Layout.fillWidth: true
                    text: "Deleting a member removes them and their membership for good."
                    color: theme.muted
                    font.pixelSize: 13
                    wrapMode: Text.WordWrap
                }
            }
            SharpButton {
                text: "Delete member"
                danger: true
                enabled: panel.member.id !== undefined
                onClicked: confirmDialog.ask(
                    "delete",
                    "Delete member",
                    "Permanently delete " + (panel.member.fullName || "this member")
                        + "? This can't be undone.",
                    "Delete")
            }
        }
    }

    // =======================================================================
    // Pop-up: pick a plan (used for both "add" and "change")
    // =======================================================================
    Popup {
        id: planDialog

        property string heading: ""
        property int selected: 0

        function openFor(title, currentMonths) {
            heading = title
            selected = currentMonths
            open()
        }

        parent: Overlay.overlay
        anchors.centerIn: parent
        modal: true
        focus: true
        padding: 28
        width: 460
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside

        Overlay.modal: Rectangle { color: "#c0000000" }

        enter: Transition { NumberAnimation { property: "opacity"; from: 0.0; to: 1.0; duration: 120 } }
        exit: Transition { NumberAnimation { property: "opacity"; from: 1.0; to: 0.0; duration: 90 } }

        background: Rectangle {
            color: theme.surface
            border.width: 1
            border.color: theme.accent
        }

        contentItem: ColumnLayout {
            spacing: 18

            Text {
                text: planDialog.heading
                color: theme.text
                font.pixelSize: 24
                font.weight: Font.Bold
                font.capitalization: Font.AllUppercase
            }
            SectionLabel { text: "Choose a plan — it starts today" }

            GridLayout {
                Layout.fillWidth: true
                columns: 2
                rowSpacing: 10
                columnSpacing: 10

                Repeater {
                    model: backend.plans

                    delegate: Rectangle {
                        id: tile
                        required property var modelData
                        readonly property bool picked: planDialog.selected === modelData

                        Layout.fillWidth: true
                        Layout.preferredWidth: 1
                        Layout.preferredHeight: 84
                        color: picked ? theme.accent : (tileMouse.containsMouse ? theme.surfaceHi : "transparent")
                        border.width: 1
                        border.color: picked ? theme.accent : theme.border

                        ColumnLayout {
                            anchors.centerIn: parent
                            spacing: 0

                            Text {
                                Layout.alignment: Qt.AlignHCenter
                                text: tile.modelData
                                color: tile.picked ? theme.onAccent : theme.text
                                font.pixelSize: 34
                                font.weight: Font.Bold
                            }
                            Text {
                                Layout.alignment: Qt.AlignHCenter
                                text: tile.modelData === 1 ? "MONTH" : "MONTHS"
                                color: tile.picked ? theme.onAccent : theme.muted
                                font.pixelSize: 11
                                font.letterSpacing: 2
                            }
                        }

                        MouseArea {
                            id: tileMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: planDialog.selected = tile.modelData
                        }
                    }
                }
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 10

                SharpButton {
                    Layout.fillWidth: true
                    Layout.preferredWidth: 1
                    text: "Cancel"
                    onClicked: planDialog.close()
                }
                SharpButton {
                    Layout.fillWidth: true
                    Layout.preferredWidth: 1
                    text: "Confirm"
                    primary: true
                    enabled: planDialog.selected > 0
                    onClicked: {
                        backend.setMembership(panel.memberId, planDialog.selected)
                        planDialog.close()
                    }
                }
            }
        }
    }

    // =======================================================================
    // Pop-up: "are you sure?" (used for cancel membership and delete member)
    // =======================================================================
    Popup {
        id: confirmDialog

        property string action: ""
        property string heading: ""
        property string body: ""
        property string confirmText: "Confirm"

        function ask(kind, title, message, buttonText) {
            action = kind
            heading = title
            body = message
            confirmText = buttonText
            open()
        }

        parent: Overlay.overlay
        anchors.centerIn: parent
        modal: true
        focus: true
        padding: 28
        width: 440
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside

        Overlay.modal: Rectangle { color: "#c0000000" }

        enter: Transition { NumberAnimation { property: "opacity"; from: 0.0; to: 1.0; duration: 120 } }
        exit: Transition { NumberAnimation { property: "opacity"; from: 1.0; to: 0.0; duration: 90 } }

        background: Rectangle {
            color: theme.surface
            border.width: 1
            border.color: theme.danger
        }

        contentItem: ColumnLayout {
            spacing: 16

            Text {
                text: confirmDialog.heading
                color: theme.text
                font.pixelSize: 24
                font.weight: Font.Bold
                font.capitalization: Font.AllUppercase
            }
            Text {
                Layout.fillWidth: true
                text: confirmDialog.body
                color: theme.muted
                font.pixelSize: 15
                wrapMode: Text.WordWrap
            }

            RowLayout {
                Layout.fillWidth: true
                Layout.topMargin: 6
                spacing: 10

                SharpButton {
                    Layout.fillWidth: true
                    Layout.preferredWidth: 1
                    text: "Go back"
                    onClicked: confirmDialog.close()
                }
                SharpButton {
                    Layout.fillWidth: true
                    Layout.preferredWidth: 1
                    text: confirmDialog.confirmText
                    danger: true
                    onClicked: {
                        var kind = confirmDialog.action
                        var targetId = panel.memberId
                        confirmDialog.close()
                        if (kind === "cancel") {
                            backend.cancelMembership(targetId)
                        } else if (kind === "delete") {
                            backend.deleteMember(targetId)
                            panel.memberDeleted(targetId)
                        }
                    }
                }
            }
        }
    }
}
