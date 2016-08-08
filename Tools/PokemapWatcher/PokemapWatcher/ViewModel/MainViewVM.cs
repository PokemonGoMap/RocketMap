using PokemapWatcher.Commands;
using PokemapWatcher.Model;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Input;

namespace PokemapWatcher.ViewModel
{
    public class MainViewVM : INotifyPropertyChanged
    {
        public MainViewVM()
        {
            ServerList = new ObservableCollection<WebserverInstance>(SettingsProvider.readSettings());

            #region Commands
            CloseCommand = new RelayCommand(Close);

            CreateServerCommand = new RelayCommand(CreateServer);
            DeleteServerCommand = new RelayCommand(DeleteServer);

            SaveSettingsCommand = new RelayCommand(SaveSettings);
                                    
            StartProcAllCommand = new RelayCommand(StartProcAll);
            StopProcAllCommand = new RelayCommand(StopProcAll);
            #endregion
        }

        #region Commands
        private ICommand m_CloseCommand;
        public ICommand CloseCommand
        {
            get { return m_CloseCommand; }
            set
            {
                m_CloseCommand = value;
                NotifyPropertyChanged();
            }
        }
        private void Close(object o)
        {
            StopProcAllCommand.Execute(null);
        }


        private ICommand m_CreateServerCommand;
        public ICommand CreateServerCommand
        {
            get { return m_CreateServerCommand; }
            set
            {
                m_CreateServerCommand = value;
                NotifyPropertyChanged();
            }
        }
        private void CreateServer(object o)
        {
            ServerList.Add(new WebserverInstance());
        }

        private ICommand m_DeleteServerCommand;
        public ICommand DeleteServerCommand
        {
            get { return m_DeleteServerCommand; }
            set
            {
                m_DeleteServerCommand = value;
                NotifyPropertyChanged();
            }
        }
        private void DeleteServer(object o)
        {
            if (SelectedServer != null)
            {
                var s = SelectedServer;
                SelectedServer = null;
                ServerList.Remove(s);
            }
        }
        

        private ICommand m_SaveSettingsCommand;
        public ICommand SaveSettingsCommand
        {
            get { return m_SaveSettingsCommand; }
            set
            {
                m_SaveSettingsCommand = value;
                NotifyPropertyChanged();
            }
        }
        private void SaveSettings (object o)
        {
            SettingsProvider.writeSettings(new List<WebserverInstance>(ServerList));
        }
                

        private ICommand m_StartProcAllCommand;
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
            foreach (WebserverInstance ins in ServerList)
            {
                ins.Start();
                foreach(WorkerInstance ins2 in ins.WorkerInstanceCollection)
                {
                    ins2.Start();
                }
            }
        }

        private ICommand m_StopProcAllCommand;
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
            foreach (WebserverInstance ins in ServerList)
            {
                ins.Stop();
                foreach (WorkerInstance ins2 in ins.WorkerInstanceCollection)
                {
                    ins2.Stop();
                }
            }
        }
        #endregion

        #region Member
        private ObservableCollection<WebserverInstance> m_ServerList;        
        public ObservableCollection<WebserverInstance> ServerList
        {
            get { return m_ServerList; }
            set
            {
                m_ServerList = value;
                NotifyPropertyChanged();
            }
        }

        private WebserverInstance m_SelectedServer;
        public WebserverInstance SelectedServer
        {
            get { return m_SelectedServer; }
            set
            {
                m_SelectedServer = value;
                NotifyPropertyChanged();
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
