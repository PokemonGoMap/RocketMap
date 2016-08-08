using PokemapWatcher.Commands;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Diagnostics;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Input;
using System.Xml.Serialization;

namespace PokemapWatcher.Model
{
    public enum AuthService
    {
        ptc,
        google,
    }

    public enum Locale
    {
        en,
        de,
        fr,
        ja,
        pt_br,
        ru,
        zh_cn,
        zh_hk,
        zh_tw,
    }

    public abstract class AbstractInstance : INotifyPropertyChanged
    {
        public AbstractInstance()
        {
            StartProcCommand = new RelayCommand(StartProc);
            StopProcCommand = new RelayCommand(StopProc);
        }

        #region Commands
        [XmlIgnore]
        private ICommand m_StartProcCommand;
        [XmlIgnore]
        public ICommand StartProcCommand
        {
            get { return m_StartProcCommand; }
            set
            {
                m_StartProcCommand = value;
                NotifyPropertyChanged();
            }
        }
        private void StartProc(object o)
        {
            Start();
        }

        [XmlIgnore]
        private ICommand m_StopProcCommand;
        [XmlIgnore]
        public ICommand StopProcCommand
        {
            get { return m_StopProcCommand; }
            set
            {
                m_StopProcCommand = value;
                NotifyPropertyChanged();
            }
        }
        private void StopProc(object o)
        {
            Stop();
        }
        #endregion

        #region Global Data
        [XmlIgnore]
        string m_InstanceName = "New Pokemon GO Map Instance";
        [XmlAttribute]
        public string InstanceName
        {
            get { return m_InstanceName; }
            set
            {
                m_InstanceName = value;
                NotifyPropertyChanged();
            }
        }

        [XmlIgnore]
        string m_GoogleMapsKey = "put your gmaps-key here";
        [XmlAttribute]
        public string GoogleMapsKey
        {
            get { return m_GoogleMapsKey; }
            set
            {
                m_GoogleMapsKey = value;
                NotifyPropertyChanged();
                RefreshGMapsKey(GoogleMapsKey);
            }
        }

        [XmlIgnore]
        string m_Location = "latitude longitude";
        [XmlAttribute]
        public string Location
        {
            get { return m_Location; }
            set
            {
                m_Location = value;
                LocationHyperlink = "";
                NotifyPropertyChanged();
            }
        }

        [XmlIgnore]
        public string LocationHyperlink
        {
            get
            {
                var first = Location.Substring(0, Location.IndexOf(' '));
                var scnd = Location.Substring(Location.IndexOf(' ') + 1, Location.Length - (Location.IndexOf(' ') + 1));
                return "http://www.google.com/maps/place/" + first + "," + scnd;
            }
            set
            {
                NotifyPropertyChanged();
            }
        }

        [XmlIgnore]
        Locale m_Language = Locale.en;
        [XmlAttribute]
        public Locale Language
        {
            get { return m_Language; }
            set
            {
                m_Language = value;
                NotifyPropertyChanged();
            }
        }
        #endregion
        
        #region Member
        [XmlIgnore]
        private ObservableCollection<string> m_ProcOutput = new ObservableCollection<string>();
        [XmlIgnore]
        public ObservableCollection<string> ProcOutput
        {
            get { return m_ProcOutput; }
            set
            {
                m_ProcOutput = value;
                NotifyPropertyChanged();
            }
        }

        [XmlIgnore]
        private bool m_Running = false;
        [XmlIgnore]
        public bool Running
        {
            get { return m_Running; }
            set
            {
                m_Running = value;
                NotifyPropertyChanged();
            }
        }
        [XmlIgnore]
        private bool m_NotRunning = true;
        [XmlIgnore]
        public bool NotRunning
        {
            get { return m_NotRunning; }
            set
            {
                m_NotRunning = value;
                NotifyPropertyChanged();
            }
        }

        [XmlIgnore]
        private Process Proc = null;
        #endregion

        #region Methods
        public void Start()
        {
            if (Proc == null)
            {
                Running = true;
                NotRunning = false;
                ProcOutput.Clear();
                ProcOutput.Add("Starting Instance");
                // Init Proc
                Proc = new Process();
                Proc.StartInfo.FileName = @"C:\Python27\python.exe";
                #region Arguments
                string args = "runserver.py ";
                args += "-L " + Language.ToString() + " ";
                // Google Maps Key
                args += "-k " + GoogleMapsKey + " ";
                // Location
                args += "-l \"" + Location + "\" ";
                // Arguments of Instance derivate
                args += BuildProcArguments();
                #endregion
                Proc.StartInfo.Arguments = args;
                ProcOutput.Add("Run Pokemon GO Map Instance with args:");
                ProcOutput.Add(Proc.StartInfo.Arguments);
                ProcOutput.Insert(0, " ");
                ProcOutput.Insert(0, "------------------");
                ProcOutput.Insert(0, " ");
                Proc.StartInfo.UseShellExecute = false;
                Proc.StartInfo.RedirectStandardOutput = true;
                Proc.StartInfo.RedirectStandardError = true;
                Proc.StartInfo.CreateNoWindow = true;
                Proc.OutputDataReceived += Proc_OutputDataReceived;
                Proc.ErrorDataReceived += Proc_ErrorDataReceived;
                Proc.Exited += Proc_Exited;
                Proc.Start();
                Proc.BeginOutputReadLine();
                Proc.BeginErrorReadLine();
            }
        }
        public void Stop()
        {
            if (Proc != null)
            {
                Running = false;
                NotRunning = true;
                try
                {
                    Proc.Kill();
                }
                catch (Exception e)
                {
                    // Ignore
                }
                Proc = null;
            }
        }

        abstract public string BuildProcArguments();
        
        private void Proc_Exited(object sender, EventArgs e)
        {
            Stop();
        }
        private void Proc_OutputDataReceived(object sender, DataReceivedEventArgs e)
        {
            if (!String.IsNullOrEmpty(e.Data))
                Application.Current.Dispatcher.Invoke((Action)(() =>
                {
                    ProcOutput.Insert(0, e.Data);
                    //ProcOutput.Add(e.Data);
                    while (ProcOutput.Count > 200)
                        //ProcOutput.RemoveAt(0);
                        ProcOutput.RemoveAt(ProcOutput.Count - 1);
                }));
        }
        private void Proc_ErrorDataReceived(object sender, DataReceivedEventArgs e)
        {
            if (!String.IsNullOrEmpty(e.Data))
                Application.Current.Dispatcher.Invoke((Action)(() =>
                {
                    ProcOutput.Insert(0, e.Data);
                    //ProcOutput.Add(e.Data);
                    while (ProcOutput.Count > 200)
                        //ProcOutput.RemoveAt(0);
                        ProcOutput.RemoveAt(ProcOutput.Count - 1);
                }));
        }

        abstract public void RefreshGMapsKey(string key);
        #endregion

        #region INotifyPropertyChanged
        public event PropertyChangedEventHandler PropertyChanged;
        private void NotifyPropertyChanged([CallerMemberName] string PropertyName = null)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(PropertyName));
        }
        #endregion
    }
}
