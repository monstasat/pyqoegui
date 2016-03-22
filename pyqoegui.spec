%define debug_package %{nil}

Summary:        ats-analyzer gui
Name:           pyqoegui
Version:        0.5.0b
Release:        1%{?dist}
License:        Proprietary
Group:          Applications/Multimedia
URL:            http://www.niitv.ru/
Source0:        %{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}

BuildRequires:  python3-pyserial
BuildRequires:  python3-psutil

%description

%prep

%setup -q -c -T -a 0

%build

%install
%{__mkdir_p} '%{buildroot}/opt/'
%{__mkdir_p} '%{buildroot}/usr/bin/'

cp ./%{name}/ats.sh %{buildroot}/usr/bin/
cp ./%{name}/*.py %{buildroot}/opt/
cp -R ./%{name}/Control %{buildroot}/opt/
cp -R ./%{name}/Config %{buildroot}/opt/
cp -R ./%{name}/Gui %{buildroot}/opt/
cp -R ./%{name}/Backend %{buildroot}/opt/
cp -R ./%{name}/Usb %{buildroot}/opt/

%files
/usr/bin/ats.sh
/opt/BaseInterface.py
/opt/Log.py
/opt/main.py

/opt/Backend/Backend.py
/opt/Backend/GstreamerPipeline.py
/opt/Backend/__init__.py
/opt/Backend/State.py

/opt/Config/Config.py
/opt/Config/__init__.py

/opt/Control/AnalysisSettingsIndexes.py
/opt/Control/Control.py
/opt/Control/CustomMessages.py
/opt/Control/DVBTunerControl.py
/opt/Control/__init__.py
/opt/Control/ProgramListControl.py
/opt/Control/TranslateMessages.py
/opt/Control/TunerSettingsIndexes.py

/opt/Control/ErrorDetector/AudioDataStorage.py
/opt/Control/ErrorDetector/AudioErrorDetector.py
/opt/Control/ErrorDetector/BaseErrorDetector.py
/opt/Control/ErrorDetector/StatusTypes.py
/opt/Control/ErrorDetector/VideoDataStorage.py
/opt/Control/ErrorDetector/VideoErrorDetector.py

/opt/Gui/ButtonToolbar.py
/opt/Gui/DumpSettingsDialog.py
/opt/Gui/Icon.py
/opt/Gui/Placeholder.py
/opt/Gui/Spacing.py
/opt/Gui/BaseDialog.py
/opt/Gui/Gui.py
/opt/Gui/__init__.py
/opt/Gui/ProgramTreeModel.py

/opt/Gui/AboutDialog/AboutDialog.py
/opt/Gui/AboutDialog/__init__.py
/opt/Gui/AboutDialog/logo_square.png

/opt/Gui/AllResultsPage/AllResultsPage.py
/opt/Gui/AllResultsPage/__init__.py

/opt/Gui/AnalysisSettingsDialog/AnalysisSettingsDialog.py
/opt/Gui/AnalysisSettingsDialog/AnalysisSettingsPage.py
/opt/Gui/AnalysisSettingsDialog/__init__.py

/opt/Gui/CurrentResultsPage/CurrentResultsPage.py
/opt/Gui/CurrentResultsPage/__init__.py
/opt/Gui/CurrentResultsPage/ProgramTable.py
/opt/Gui/CurrentResultsPage/RendererGrid.py
/opt/Gui/CurrentResultsPage/Renderer.py

/opt/Gui/PlotPage/__init__.py
/opt/Gui/PlotPage/PlotPage.py
/opt/Gui/PlotPage/PlotProgramTreeView.py
/opt/Gui/PlotPage/PlotTypeSelectDialog.py
/opt/Gui/PlotPage/PlotTypes.py

/opt/Gui/PlotPage/Plot/GraphTypes.py
/opt/Gui/PlotPage/Plot/__init__.py
/opt/Gui/PlotPage/Plot/PlotBottomBar.py
/opt/Gui/PlotPage/Plot/Plot.py

/opt/Gui/ProgramSelectDialog/__init__.py
/opt/Gui/ProgramSelectDialog/ProgramSelectDialog.py
/opt/Gui/ProgramSelectDialog/ProgramTreeView.py

/opt/Gui/TunerSettingsDialog/CableFrequencyModel.py
/opt/Gui/TunerSettingsDialog/__init__.py
/opt/Gui/TunerSettingsDialog/TerrestrialFrequencyModel.py
/opt/Gui/TunerSettingsDialog/TunerMeasuredDataTreeView.py
/opt/Gui/TunerSettingsDialog/TunerSettingsBox.py
/opt/Gui/TunerSettingsDialog/TunerSettingsDialog.py
/opt/Gui/TunerSettingsDialog/TunerStatusBox.py
/opt/Gui/TunerSettingsDialog/TunerStatusTreeView.py

/opt/Usb/__init__.py
/opt/Usb/UsbExchange.py
/opt/Usb/UsbMessageParser.py
/opt/Usb/UsbMessageTypes.py
/opt/Usb/Usb.py


%changelog

