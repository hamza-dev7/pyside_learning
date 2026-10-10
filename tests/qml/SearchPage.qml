import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: page

    property int foundId: -1          // -1 = nothing to show
    property string message: ""
    property bool messageIsError: false

    function search() {
        var text = idField.text.trim()
        if (text === "") {
            foundId = -1
            messageIsError = true
            message = "Enter a member ID."
            return
        }
        var wantedId = parseInt(text, 10)
        var member = backend.getMember(wantedId)
        if (member.id === undefined) {
            foundId = -1
            messageIsError = true
            message = "No member found with ID " + wantedId + "."
        } else {
            message = ""
            foundId = wantedId
        }
    }

    Component.onCompleted: idField.forceActiveFocus()

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 48
        spacing: 28

        PageHeader {
            Layout.fillWidth: true
            eyebrow: "03 / Lookup"
            title: "Find by ID"
            onBackClicked: page.StackView.view.pop()
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.maximumWidth: 560
            spacing: 12

            SharpField {
                id: idField
                Layout.fillWidth: true
                placeholderText: "Member ID"
                inputMethodHints: Qt.ImhDigitsOnly
                validator: IntValidator { bottom: 1; top: 2147483647 }
                onAccepted: page.search()
            }
            SharpButton {
                text: "Search"
                primary: true
                onClicked: page.search()
            }
        }

        Text {
            visible: text !== ""
            text: page.message
            color: page.messageIsError ? theme.danger : theme.muted
            font.pixelSize: 14
        }

        // the same info panel used by the "Member info" page
        MemberInfoPanel {
            Layout.fillWidth: true
            Layout.maximumWidth: 760
            visible: page.foundId > 0
            memberId: page.foundId
            onMemberDeleted: (deletedId) => {
                page.foundId = -1
                page.messageIsError = false
                page.message = "Member " + deletedId + " was deleted."
            }
        }

        Item { Layout.fillHeight: true }
    }
}
