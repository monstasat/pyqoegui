VERSION=0.5.0b
all:
	tar czvf /tmp/pyqoegui-$(VERSION).tar.gz ../pyqoegui/{ats.sh,main.py,BaseInterface.py,Log.py,Backend,Config,Control,Gui,Usb}
	mv /tmp/pyqoegui-$(VERSION).tar.gz ./
