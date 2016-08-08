using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Text;
using System.Threading.Tasks;
using System.Xml.Serialization;

namespace PokemapWatcher.Model
{
    public class WorkerInstance : AbstractInstance, INotifyPropertyChanged
    {
        public WorkerInstance ()
        {
            InstanceName = "New Worker Instance";
        }

        #region Searcher Settings
        [XmlIgnore]
        AuthService m_AuthService = AuthService.ptc;
        [XmlAttribute]
        public AuthService AuthService
        {
            get { return m_AuthService; }
            set
            {
                m_AuthService = value;
                NotifyPropertyChanged();
            }
        }

        [XmlIgnore]
        string m_Username = "";
        [XmlAttribute]
        public string Username
        {
            get { return m_Username; }
            set
            {
                m_Username = value;
                NotifyPropertyChanged();
            }
        }

        [XmlIgnore]
        string m_Password = "";
        [XmlAttribute]
        public string Password
        {
            get { return m_Password; }
            set
            {
                m_Password = value;
                NotifyPropertyChanged();
            }
        }

        [XmlIgnore]
        public UInt16 m_StepLimit = 5;
        [XmlAttribute]
        public UInt16 StepLimit
        {
            get { return m_StepLimit; }
            set
            {
                m_StepLimit = value;
                NotifyPropertyChanged();
            }
        }

        [XmlIgnore]
        public UInt16 m_StepDelay = 5;
        [XmlAttribute]
        public UInt16 StepDelay
        {
            get { return m_StepDelay; }
            set
            {
                m_StepDelay = value;
                NotifyPropertyChanged();
            }
        }
        #endregion
        
        #region Methods
        public override string BuildProcArguments()
        {
            string args = "";

            args += "--no-server ";
            if (AuthService == AuthService.ptc)
                args += "-a ptc ";
            else if (AuthService == AuthService.google)
                args += "-a google ";
            // Username
            args += "-u " + Username + " ";
            // Password
            args += "-p " + Password + " ";
            // Step Limit
            args += "-st " + StepLimit + " ";
            // Step Delay
            args += "-sd " + StepDelay + " ";

            return args;
        }
        public override void RefreshGMapsKey(string key)
        {
            return;
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
