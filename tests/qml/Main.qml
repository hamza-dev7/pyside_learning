import QtQuick
import QtQuick.Controls

ApplicationWindow {
    id: window

    visible: true
    width: 1040
    height: 720
    minimumWidth: 820
    minimumHeight: 600
    title: "Gym Management"
    color: theme.bg

    background: Rectangle { color: theme.bg }

    // Pages are pushed on / popped off this stack.
    StackView {
        id: stack
        anchors.fill: parent
        initialItem: "HomePage.qml"

        pushEnter: Transition {
            ParallelAnimation {
                NumberAnimation { property: "opacity"; from: 0; to: 1; duration: 200 }
                NumberAnimation { property: "x"; from: 40; to: 0; duration: 200; easing.type: Easing.OutCubic }
            }
        }
        pushExit: Transition {
            NumberAnimation { property: "opacity"; from: 1; to: 0; duration: 140 }
        }
        popEnter: Transition {
            NumberAnimation { property: "opacity"; from: 0; to: 1; duration: 200 }
        }
        popExit: Transition {
            ParallelAnimation {
                NumberAnimation { property: "opacity"; from: 1; to: 0; duration: 140 }
                NumberAnimation { property: "x"; from: 0; to: 40; duration: 140; easing.type: Easing.InCubic }
            }
        }
    }
}
