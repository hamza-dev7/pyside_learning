import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: page

    // set by StackView.push("MemberInfoPage.qml", { memberId: ... })
    property int memberId: -1

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 48
        spacing: 28

        PageHeader {
            Layout.fillWidth: true
            eyebrow: "Directory / Member"
            title: "Member info"
            backText: "Members"
            onBackClicked: page.StackView.view.pop()
        }

        MemberInfoPanel {
            Layout.fillWidth: true
            Layout.maximumWidth: 760
            memberId: page.memberId
            onMemberDeleted: page.StackView.view.pop()
        }

        Item { Layout.fillHeight: true }
    }
}
