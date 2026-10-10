import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: page

    property string message: ""
    property bool messageIsError: false

    function save() {
        var name = nameField.text.trim().replace(/\s+/g, " ")
        if (name === "") {
            messageIsError = true
            message = "Please enter the member's full name."
            nameField.forceActiveFocus()
            return
        }
        var newId = backend.addMember(name, phoneField.text.trim())
        messageIsError = false
        message = "Member added. Their ID is " + newId + "."
        nameField.clear()
        phoneField.clear()
        nameField.forceActiveFocus()
    }

    Component.onCompleted: nameField.forceActiveFocus()

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 48
        spacing: 28

        PageHeader {
            Layout.fillWidth: true
            eyebrow: "01 / New"
            title: "Add a member"
            onBackClicked: page.StackView.view.pop()
        }

        ColumnLayout {
            Layout.fillWidth: true
            Layout.maximumWidth: 520
            spacing: 8

            SectionLabel { text: "Full name" }
            SharpField {
                id: nameField
                Layout.fillWidth: true
                placeholderText: "e.g. John Smith"
                onAccepted: page.save()
            }

            Item { Layout.preferredHeight: 10 }

            SectionLabel { text: "Phone (optional)" }
            SharpField {
                id: phoneField
                Layout.fillWidth: true
                placeholderText: "e.g. 0612345678"
                onAccepted: page.save()
            }

            Item { Layout.preferredHeight: 14 }

            SharpButton {
                Layout.fillWidth: true
                text: "Save member"
                primary: true
                onClicked: page.save()
            }

            Text {
                Layout.fillWidth: true
                visible: text !== ""
                text: page.message
                color: page.messageIsError ? theme.danger : theme.accent
                font.pixelSize: 14
                wrapMode: Text.WordWrap
            }
        }

        Item { Layout.fillHeight: true }
    }
}
