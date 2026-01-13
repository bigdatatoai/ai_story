<template>
  <div id="app">
    <NetworkStatus />
    <NotificationDisplay />
    <router-view />
  </div>
</template>

<script>
import NetworkStatus from '@/components/NetworkStatus/NetworkStatus.vue';
import NotificationDisplay from '@/components/NotificationDisplay/NotificationDisplay.vue';
import networkMonitor from '@/services/networkMonitor';
import notificationService from '@/services/notificationService';

export default {
  name: 'App',
  components: {
    NetworkStatus,
    NotificationDisplay,
  },
  mounted() {
    this.initNetworkMonitoring();
  },
  methods: {
    initNetworkMonitoring() {
      networkMonitor.subscribe({
        onOnline: ({ offlineDuration }) => {
          notificationService.networkStatus(true, offlineDuration);
        },
        onOffline: () => {
          notificationService.networkStatus(false);
        },
      });
    },
  },
};
</script>

<style scoped>
#app {
  width: 100%;
  height: 100%;
}
</style>
