using PokemapWatcher.Commands;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Input;
using System.Xml.Serialization;

namespace PokemapWatcher.Model
{
    public class WebserverInstance : AbstractInstance, INotifyPropertyChanged
    {
        public WebserverInstance()
        {
            InstanceName = "new Server";
            
            CreateNewInstanceCommand = new RelayCommand(CreateNewInstance);
            DeleteInstanceCommand = new RelayCommand(DeleteInstance);
            StartProcAllCommand = new RelayCommand(StartProcAll);
            StopProcAllCommand = new RelayCommand(StopProcAll);
        }

        #region Server Settings
        string m_Host = "hostname";
        [XmlAttribute]
        public string Host
        {
            get { return m_Host; }
            set
            {
                m_Host = value;
                NotifyPropertyChanged();
            }
        }

        [XmlIgnore]
        UInt16 m_Port = 8080;
        [XmlAttribute]
        public UInt16 Port
        {
            get { return m_Port; }
            set
            {
                m_Port = value;
                NotifyPropertyChanged();
            }
        }

        [XmlIgnore]
        bool m_FixedLocation = true;
        [XmlAttribute]
        public bool FixedLocation
        {
            get { return m_FixedLocation; }
            set
            {
                m_FixedLocation = value;
                NotifyPropertyChanged();
            }
        }
        #endregion
        
        #region Member
        [XmlIgnore]
        private ObservableCollection<WorkerInstance> m_WorkerInstanceCollection = new ObservableCollection<WorkerInstance>();
        [XmlArray]
        public ObservableCollection<WorkerInstance> WorkerInstanceCollection
        {
            get { return m_WorkerInstanceCollection; }
            set
            {
                m_WorkerInstanceCollection = value;
                NotifyPropertyChanged();
            }
        }

        [XmlIgnore]
        private WorkerInstance m_SelectedInstance;
        [XmlIgnore]
        public WorkerInstance SelectedInstance
        {
            get { return m_SelectedInstance; }
            set
            {
                m_SelectedInstance = value;
                NotifyPropertyChanged();
            }
        }
        #endregion

        #region Methods
        public override string BuildProcArguments()
        {
            string args = "";

            args += "--only-server ";
            // IP
            args += "-H " + Host + " ";
            // Port
            args += "-P " + Port + " ";
            // Fixed Location
            if (FixedLocation)
                args += "-fl ";

            return args;
        }
        public override void RefreshGMapsKey(string key)
        {
            WorkerInstanceCollection?.All(m => { m.GoogleMapsKey = GoogleMapsKey; return true; });
        }
        #endregion

        #region Commands
        [XmlIgnore]
        private ICommand m_CreateNewInstanceCommand;
        [XmlIgnore]
        public ICommand CreateNewInstanceCommand
        {
            get { return m_CreateNewInstanceCommand; }
            set
            {
                m_CreateNewInstanceCommand = value;
                NotifyPropertyChanged();
            }
        }
        private void CreateNewInstance(object o)
        {
            var i = new WorkerInstance();
            WorkerInstanceCollection.Add(i);
            SelectedInstance = i;
            i.GoogleMapsKey = GoogleMapsKey;
            i.Location = Location;
        }

        [XmlIgnore]
        private ICommand m_DeleteInstanceCommand;
        [XmlIgnore]
        public ICommand DeleteInstanceCommand
        {
            get { return m_DeleteInstanceCommand; }
            set
            {
                m_DeleteInstanceCommand = value;
                NotifyPropertyChanged();
            }
        }
        private void DeleteInstance(object o)
        {
            var i = SelectedInstance;
            SelectedInstance = null;
            WorkerInstanceCollection.Remove(i);
        }
        
        [XmlIgnore]
        private ICommand m_StartProcAllCommand;
        [XmlIgnore]
        public ICommand StartProcAllCommand
        {
            get { return m_StartProcAllCommand; }
            set
            {
                m_StartProcAllCommand = value;
                NotifyPropertyChanged();
            }
        }
        private void StartProcAll(object o)
        {
            foreach (WorkerInstance ins in WorkerInstanceCollection)
            {
                ins.Start();
            }
        }

        [XmlIgnore]
        private ICommand m_StopProcAllCommand;
        [XmlIgnore]
        public ICommand StopProcAllCommand
        {
            get { return m_StopProcAllCommand; }
            set
            {
                m_StopProcAllCommand = value;
                NotifyPropertyChanged();
            }
        }
        private void StopProcAll(object o)
        {

            foreach (WorkerInstance ins in WorkerInstanceCollection)
            {
                ins.Stop();
            }
        }
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
