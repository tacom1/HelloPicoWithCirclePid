import QtQuick
import QtQuick.Window
import "./Components"
import "./Components/FluentUI"

Window {
    width: 960
    height: 520
    visible: true
    title: qsTr("HelloPicoWithQt")
    color: "#e9ecf3"

    HelloMainContainer{
        width: 720
        height: 400

        HelloSlider{
            anchors{
                horizontalCenter: parent.horizontalCenter
                top: parent.top
                topMargin: 30
            }

            width: 460
        }
    }

}
