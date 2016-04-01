%define debug_package %{nil}

Summary:        ats-analyzer gui
Name:           pyqoegui
Version:        0.5.4b
Release:        1%{?dist}
License:        Proprietary
Group:          Applications/Multimedia
URL:            http://www.niitv.ru/
Source0:        %{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}

BuildRequires:  python3-pyserial
BuildRequires:  python3-psutil
BuildRequires:  pulseaudio-utils

%description

%prep

%setup -q -c -T -a 0

%build

%install
%{__mkdir_p} '%{buildroot}/opt/pyqoegui'
%{__mkdir_p} '%{buildroot}/usr/bin/'

cp ./%{name}/ats.sh %{buildroot}/usr/bin/
cp ./%{name}/*.py %{buildroot}/opt/%{name}/
cp -R ./%{name}/Control %{buildroot}/opt/%{name}/
cp -R ./%{name}/Config %{buildroot}/opt/%{name}/
cp -R ./%{name}/Gui %{buildroot}/opt/%{name}/
cp -R ./%{name}/Backend %{buildroot}/opt/%{name}/
cp -R ./%{name}/Usb %{buildroot}/opt/%{name}/

%files
/usr/bin/ats.sh
/opt/%{name}/BaseInterface.py
/opt/%{name}/Log.py
/opt/%{name}/main.py

/opt/%{name}/Backend/Backend.py
/opt/%{name}/Backend/GstreamerPipeline.py
/opt/%{name}/Backend/__init__.py
/opt/%{name}/Backend/State.py

/opt/%{name}/Config/Config.py
/opt/%{name}/Config/__init__.py

/opt/%{name}/Control/AnalysisSettingsIndexes.py
/opt/%{name}/Control/Control.py
/opt/%{name}/Control/CustomMessages.py
/opt/%{name}/Control/DVBTunerControl.py
/opt/%{name}/Control/__init__.py
/opt/%{name}/Control/ProgramListControl.py
/opt/%{name}/Control/TranslateMessages.py
/opt/%{name}/Control/TunerSettingsIndexes.py

/opt/%{name}/Control/ErrorDetector/AudioDataStorage.py
/opt/%{name}/Control/ErrorDetector/AudioErrorDetector.py
/opt/%{name}/Control/ErrorDetector/BaseErrorDetector.py
/opt/%{name}/Control/ErrorDetector/StatusTypes.py
/opt/%{name}/Control/ErrorDetector/VideoDataStorage.py
/opt/%{name}/Control/ErrorDetector/VideoErrorDetector.py

/opt/%{name}/Gui/ButtonToolbar.py
/opt/%{name}/Gui/DumpSettingsDialog.py
/opt/%{name}/Gui/Icon.py
/opt/%{name}/Gui/Placeholder.py
/opt/%{name}/Gui/Spacing.py
/opt/%{name}/Gui/BaseDialog.py
/opt/%{name}/Gui/Gui.py
/opt/%{name}/Gui/__init__.py
/opt/%{name}/Gui/ProgramTreeModel.py

/opt/%{name}/Gui/AboutDialog/AboutDialog.py
/opt/%{name}/Gui/AboutDialog/__init__.py
/opt/%{name}/Gui/AboutDialog/logo_square.png

/opt/%{name}/Gui/AllResultsPage/AllResultsPage.py
/opt/%{name}/Gui/AllResultsPage/__init__.py

/opt/%{name}/Gui/AnalysisSettingsDialog/AnalysisSettingsDialog.py
/opt/%{name}/Gui/AnalysisSettingsDialog/AnalysisSettingsPage.py
/opt/%{name}/Gui/AnalysisSettingsDialog/__init__.py

/opt/%{name}/Gui/CurrentResultsPage/CurrentResultsPage.py
/opt/%{name}/Gui/CurrentResultsPage/__init__.py
/opt/%{name}/Gui/CurrentResultsPage/ProgramTable.py
/opt/%{name}/Gui/CurrentResultsPage/RendererGrid.py
/opt/%{name}/Gui/CurrentResultsPage/Renderer.py

/opt/%{name}/Gui/PlotPage/__init__.py
/opt/%{name}/Gui/PlotPage/PlotPage.py
/opt/%{name}/Gui/PlotPage/PlotProgramTreeView.py
/opt/%{name}/Gui/PlotPage/PlotTypeSelectDialog.py
/opt/%{name}/Gui/PlotPage/PlotTypes.py

/opt/%{name}/Gui/PlotPage/Plot/GraphTypes.py
/opt/%{name}/Gui/PlotPage/Plot/__init__.py
/opt/%{name}/Gui/PlotPage/Plot/PlotBottomBar.py
/opt/%{name}/Gui/PlotPage/Plot/Plot.py

/opt/%{name}/Gui/ProgramSelectDialog/__init__.py
/opt/%{name}/Gui/ProgramSelectDialog/ProgramSelectDialog.py
/opt/%{name}/Gui/ProgramSelectDialog/ProgramTreeView.py

/opt/%{name}/Gui/TunerSettingsDialog/CableFrequencyModel.py
/opt/%{name}/Gui/TunerSettingsDialog/__init__.py
/opt/%{name}/Gui/TunerSettingsDialog/TerrestrialFrequencyModel.py
/opt/%{name}/Gui/TunerSettingsDialog/TunerMeasuredDataTreeView.py
/opt/%{name}/Gui/TunerSettingsDialog/TunerSettingsBox.py
/opt/%{name}/Gui/TunerSettingsDialog/TunerSettingsDialog.py
/opt/%{name}/Gui/TunerSettingsDialog/TunerStatusBox.py
/opt/%{name}/Gui/TunerSettingsDialog/TunerStatusTreeView.py

/opt/%{name}/Usb/__init__.py
/opt/%{name}/Usb/UsbExchange.py
/opt/%{name}/Usb/UsbMessageParser.py
/opt/%{name}/Usb/UsbMessageTypes.py
/opt/%{name}/Usb/Usb.py

/opt/%{name}/Backend/Backend.pyc
/opt/%{name}/Backend/Backend.pyo
/opt/%{name}/Backend/GstreamerPipeline.pyc
/opt/%{name}/Backend/GstreamerPipeline.pyo
/opt/%{name}/Backend/State.pyc
/opt/%{name}/Backend/State.pyo
/opt/%{name}/Backend/__init__.pyc
/opt/%{name}/Backend/__init__.pyo
/opt/%{name}/BaseInterface.pyc
/opt/%{name}/BaseInterface.pyo
/opt/%{name}/Config/Config.pyc
/opt/%{name}/Config/Config.pyo
/opt/%{name}/Config/__init__.pyc
/opt/%{name}/Config/__init__.pyo
/opt/%{name}/Control/AnalysisSettingsIndexes.pyc
/opt/%{name}/Control/AnalysisSettingsIndexes.pyo
/opt/%{name}/Control/Control.pyc
/opt/%{name}/Control/Control.pyo
/opt/%{name}/Control/CustomMessages.pyc
/opt/%{name}/Control/CustomMessages.pyo
/opt/%{name}/Control/DVBTunerControl.pyc
/opt/%{name}/Control/DVBTunerControl.pyo
/opt/%{name}/Control/ErrorDetector/AudioDataStorage.pyc
/opt/%{name}/Control/ErrorDetector/AudioDataStorage.pyo
/opt/%{name}/Control/ErrorDetector/AudioErrorDetector.pyc
/opt/%{name}/Control/ErrorDetector/AudioErrorDetector.pyo
/opt/%{name}/Control/ErrorDetector/BaseErrorDetector.pyc
/opt/%{name}/Control/ErrorDetector/BaseErrorDetector.pyo
/opt/%{name}/Control/ErrorDetector/StatusTypes.pyc
/opt/%{name}/Control/ErrorDetector/StatusTypes.pyo
/opt/%{name}/Control/ErrorDetector/VideoDataStorage.pyc
/opt/%{name}/Control/ErrorDetector/VideoDataStorage.pyo
/opt/%{name}/Control/ErrorDetector/VideoErrorDetector.pyc
/opt/%{name}/Control/ErrorDetector/VideoErrorDetector.pyo
/opt/%{name}/Control/ProgramListControl.pyc
/opt/%{name}/Control/ProgramListControl.pyo
/opt/%{name}/Control/TranslateMessages.pyc
/opt/%{name}/Control/TranslateMessages.pyo
/opt/%{name}/Control/TunerSettingsIndexes.pyc
/opt/%{name}/Control/TunerSettingsIndexes.pyo
/opt/%{name}/Control/__init__.pyc
/opt/%{name}/Control/__init__.pyo
/opt/%{name}/Gui/AboutDialog/AboutDialog.pyc
/opt/%{name}/Gui/AboutDialog/AboutDialog.pyo
/opt/%{name}/Gui/AboutDialog/__init__.pyc
/opt/%{name}/Gui/AboutDialog/__init__.pyo
/opt/%{name}/Gui/AllResultsPage/AllResultsPage.pyc
/opt/%{name}/Gui/AllResultsPage/AllResultsPage.pyo
/opt/%{name}/Gui/AllResultsPage/__init__.pyc
/opt/%{name}/Gui/AllResultsPage/__init__.pyo
/opt/%{name}/Gui/AnalysisSettingsDialog/AnalysisSettingsDialog.pyc
/opt/%{name}/Gui/AnalysisSettingsDialog/AnalysisSettingsDialog.pyo
/opt/%{name}/Gui/AnalysisSettingsDialog/AnalysisSettingsPage.pyc
/opt/%{name}/Gui/AnalysisSettingsDialog/AnalysisSettingsPage.pyo
/opt/%{name}/Gui/AnalysisSettingsDialog/__init__.pyc
/opt/%{name}/Gui/AnalysisSettingsDialog/__init__.pyo
/opt/%{name}/Gui/BaseDialog.pyc
/opt/%{name}/Gui/BaseDialog.pyo
/opt/%{name}/Gui/ButtonToolbar.pyc
/opt/%{name}/Gui/ButtonToolbar.pyo
/opt/%{name}/Gui/CurrentResultsPage/CurrentResultsPage.pyc
/opt/%{name}/Gui/CurrentResultsPage/CurrentResultsPage.pyo
/opt/%{name}/Gui/CurrentResultsPage/ProgramTable.pyc
/opt/%{name}/Gui/CurrentResultsPage/ProgramTable.pyo
/opt/%{name}/Gui/CurrentResultsPage/Renderer.pyc
/opt/%{name}/Gui/CurrentResultsPage/Renderer.pyo
/opt/%{name}/Gui/CurrentResultsPage/RendererGrid.pyc
/opt/%{name}/Gui/CurrentResultsPage/RendererGrid.pyo
/opt/%{name}/Gui/CurrentResultsPage/__init__.pyc
/opt/%{name}/Gui/CurrentResultsPage/__init__.pyo
/opt/%{name}/Gui/DumpSettingsDialog.pyc
/opt/%{name}/Gui/DumpSettingsDialog.pyo
/opt/%{name}/Gui/Gui.pyc
/opt/%{name}/Gui/Gui.pyo
/opt/%{name}/Gui/Icon.pyc
/opt/%{name}/Gui/Icon.pyo
/opt/%{name}/Gui/Placeholder.pyc
/opt/%{name}/Gui/Placeholder.pyo
/opt/%{name}/Gui/PlotPage/Plot/GraphTypes.pyc
/opt/%{name}/Gui/PlotPage/Plot/GraphTypes.pyo
/opt/%{name}/Gui/PlotPage/Plot/Plot.pyc
/opt/%{name}/Gui/PlotPage/Plot/Plot.pyo
/opt/%{name}/Gui/PlotPage/Plot/PlotBottomBar.pyc
/opt/%{name}/Gui/PlotPage/Plot/PlotBottomBar.pyo
/opt/%{name}/Gui/PlotPage/Plot/__init__.pyc
/opt/%{name}/Gui/PlotPage/Plot/__init__.pyo
/opt/%{name}/Gui/PlotPage/PlotPage.pyc
/opt/%{name}/Gui/PlotPage/PlotPage.pyo
/opt/%{name}/Gui/PlotPage/PlotProgramTreeView.pyc
/opt/%{name}/Gui/PlotPage/PlotProgramTreeView.pyo
/opt/%{name}/Gui/PlotPage/PlotTypeSelectDialog.pyc
/opt/%{name}/Gui/PlotPage/PlotTypeSelectDialog.pyo
/opt/%{name}/Gui/PlotPage/PlotTypes.pyc
/opt/%{name}/Gui/PlotPage/PlotTypes.pyo
/opt/%{name}/Gui/PlotPage/__init__.pyc
/opt/%{name}/Gui/PlotPage/__init__.pyo
/opt/%{name}/Gui/ProgramSelectDialog/ProgramSelectDialog.pyc
/opt/%{name}/Gui/ProgramSelectDialog/ProgramSelectDialog.pyo
/opt/%{name}/Gui/ProgramSelectDialog/ProgramTreeView.pyc
/opt/%{name}/Gui/ProgramSelectDialog/ProgramTreeView.pyo
/opt/%{name}/Gui/ProgramSelectDialog/__init__.pyc
/opt/%{name}/Gui/ProgramSelectDialog/__init__.pyo
/opt/%{name}/Gui/ProgramTreeModel.pyc
/opt/%{name}/Gui/ProgramTreeModel.pyo
/opt/%{name}/Gui/Spacing.pyc
/opt/%{name}/Gui/Spacing.pyo
/opt/%{name}/Gui/TunerSettingsDialog/CableFrequencyModel.pyc
/opt/%{name}/Gui/TunerSettingsDialog/CableFrequencyModel.pyo
/opt/%{name}/Gui/TunerSettingsDialog/TerrestrialFrequencyModel.pyc
/opt/%{name}/Gui/TunerSettingsDialog/TerrestrialFrequencyModel.pyo
/opt/%{name}/Gui/TunerSettingsDialog/TunerMeasuredDataTreeView.pyc
/opt/%{name}/Gui/TunerSettingsDialog/TunerMeasuredDataTreeView.pyo
/opt/%{name}/Gui/TunerSettingsDialog/TunerSettingsBox.pyc
/opt/%{name}/Gui/TunerSettingsDialog/TunerSettingsBox.pyo
/opt/%{name}/Gui/TunerSettingsDialog/TunerSettingsDialog.pyc
/opt/%{name}/Gui/TunerSettingsDialog/TunerSettingsDialog.pyo
/opt/%{name}/Gui/TunerSettingsDialog/TunerStatusBox.pyc
/opt/%{name}/Gui/TunerSettingsDialog/TunerStatusBox.pyo
/opt/%{name}/Gui/TunerSettingsDialog/TunerStatusTreeView.pyc
/opt/%{name}/Gui/TunerSettingsDialog/TunerStatusTreeView.pyo
/opt/%{name}/Gui/TunerSettingsDialog/__init__.pyc
/opt/%{name}/Gui/TunerSettingsDialog/__init__.pyo
/opt/%{name}/Gui/__init__.pyc
/opt/%{name}/Gui/__init__.pyo
/opt/%{name}/Log.pyc
/opt/%{name}/Log.pyo
/opt/%{name}/Usb/Usb.pyc
/opt/%{name}/Usb/Usb.pyo
/opt/%{name}/Usb/UsbExchange.pyc
/opt/%{name}/Usb/UsbExchange.pyo
/opt/%{name}/Usb/UsbMessageParser.pyc
/opt/%{name}/Usb/UsbMessageParser.pyo
/opt/%{name}/Usb/UsbMessageTypes.pyc
/opt/%{name}/Usb/UsbMessageTypes.pyo
/opt/%{name}/Usb/__init__.pyc
/opt/%{name}/Usb/__init__.pyo
/opt/%{name}/main.pyc
/opt/%{name}/main.pyo



%changelog

