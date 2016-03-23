VERSION=0.5.1b
all:
	find . -name "__pycache__" | xargs rm -rf {}
	tar czvf /tmp/pyqoegui-$(VERSION).tar.gz ../pyqoegui/{ats.sh,main.py,BaseInterface.py,Log.py,Backend,Config,Control,Gui,Usb}
	mv /tmp/pyqoegui-$(VERSION).tar.gz ./
