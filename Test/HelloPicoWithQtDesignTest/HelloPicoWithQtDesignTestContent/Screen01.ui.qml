

/*
This is a UI file (.ui.qml) that is intended to be edited in Qt Design Studio only.
It is supposed to be strictly declarative and only uses a subset of QML. If you edit
this file manually, you might introduce QML code that is not supported by Qt Design Studio.
Check out https://doc.qt.io/qtcreator/creator-quick-ui-forms.html for details on .ui.qml files.
*/
import QtQuick
import QtQuick.Controls
import HelloPicoWithQtDesignTest

Rectangle {
    id: rectangle
    width: Constants.width
    height: Constants.height
    color: "#ecf0f4"

    Rectangle {
        id: rectangle1
        width: 720
        height: 400
        color: "#f3f4f8"
        radius: 10
        border.color: "#ec0e0e"
        anchors.centerIn: parent

        Text {
            id: text1
            text: qsTr("Linear Motor Control")
            anchors.top: parent.top
            anchors.topMargin: -68
            font.pixelSize: 32
            anchors.horizontalCenterOffset: 0
            font.weight: Font.Bold
            anchors.horizontalCenter: parent.horizontalCenter
        }

        Slider {
            id: slider
            y: 52
            width: 460
            value: 0.5
            anchors.horizontalCenterOffset: 0
            anchors.horizontalCenter: parent.horizontalCenter

            Text {
                id: text2
                text: qsTr("0.00mm")
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.leftMargin: -100
                font.pixelSize: 24
            }

            Text {
                id: text3
                text: qsTr("20.10mm")
                anchors.verticalCenter: parent.verticalCenter
                anchors.right: parent.right
                anchors.rightMargin: -110
                font.pixelSize: 24
            }

            Text {
                id: text4
                text: qsTr("10.05mm")
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.topMargin: -35
                anchors.bottomMargin: 44
                font.pixelSize: 24
                anchors.horizontalCenter: parent.horizontalCenter
            }
        }

        Rectangle {
            id: rectangle2
            width: parent.width / 2 - 60
            height: 160
            color: "#ffffff"
            border.color: "#ec0e0e"
            anchors.left: parent.left
            anchors.top: slider.bottom
            anchors.leftMargin: 24
            anchors.topMargin: 32

            Text {
                id: text5
                text: qsTr("Set Positon")
                anchors.left: parent.left
                anchors.top: parent.top
                anchors.leftMargin: 0
                anchors.topMargin: 0
                font.pixelSize: 24
            }

            Text {
                id: text6
                text: qsTr("10mm")
                anchors.left: slider1.left
                anchors.top: text5.bottom
                anchors.bottom: slider1.top
                anchors.leftMargin: 0
                anchors.topMargin: 0
                anchors.bottomMargin: 0
                font.pixelSize: 32
                verticalAlignment: Text.AlignVCenter
            }

            Slider {
                id: slider1
                width: parent.width - 40
                value: 0.5
                anchors.bottom: parent.bottom
                anchors.bottomMargin: 20
                anchors.horizontalCenter: parent.horizontalCenter
            }
        }

        Rectangle {
            id: rectangle3
            width: parent.width / 2 - 60
            height: 160
            color: "#ffffff"
            border.color: "#ec0e0e"
            anchors.right: parent.right
            anchors.top: slider.bottom
            anchors.rightMargin: 24
            anchors.topMargin: 32
            Text {
                id: text7
                text: qsTr("Speed Measure")
                anchors.left: parent.left
                anchors.top: parent.top
                anchors.leftMargin: 0
                anchors.topMargin: 0
                font.pixelSize: 24
            }

            Text {
                id: text8
                text: qsTr("3.21 mm/s")
                font.pixelSize: 48
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                anchors.centerIn: parent
            }
        }

        Button {
            id: button
            width: parent.width - 60
            text: qsTr("Send Position")
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 20
            font.pointSize: 24
            anchors.horizontalCenter: parent.horizontalCenter
            background: Rectangle{
                color: "#50a8f0"
            }
        }
    }
    states: [
        State {
            name: "clicked"
        }
    ]
}
