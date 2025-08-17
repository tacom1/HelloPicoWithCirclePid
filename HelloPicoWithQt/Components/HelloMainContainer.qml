import QtQuick
import "./FluentUI"

Rectangle{
    id: centerControl
    color: "#f3f4f9"
    radius: 15
    FluShadow{
        radius: 15
    }
    anchors.centerIn: parent

    FluText{
        text: "Linear Motor Control"
        color: "#374657"
        font.bold: true
        font.pixelSize: 23

        anchors{
            horizontalCenter: centerControl.horizontalCenter
            bottom: centerControl.top
            bottomMargin: 8
        }
    }
}


