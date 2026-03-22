import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Alert } from 'react-native';
import { practiceService, awardService } from '../services';

export function ParentDashboard({ route }) {
  const [children, setChildren] = useState([]);
  const [selectedChild, setSelectedChild] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadChildren();
  }, []);

  const loadChildren = async () => {
    try {
      setLoading(true);
      const parentInfo = route.params?.parentInfo;
      if (parentInfo?.children) {
        setChildren(parentInfo.children);
        if (parentInfo.children.length > 0) {
          setSelectedChild(parentInfo.children[0]);
          loadStats(parentInfo.children[0].child_id);
        }
      }
    } catch (error) {
      Alert.alert('错误', '加载孩子信息失败');
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async (childId) => {
    try {
      const statsData = await practiceService.getStatistics(childId);
      setStats(statsData);
    } catch (error) {
      console.error('加载统计数据失败:', error);
    }
  };

  const handleGiveAward = async () => {
    if (!selectedChild) return;
    
    Alert.prompt(
      '发放游戏时间',
      '输入游戏时间（分钟）:',
      [
        {
          text: '取消',
          onPress: () => {},
          style: 'cancel',
        },
        {
          text: '确定',
          onPress: async (minutes) => {
            if (!minutes || isNaN(minutes)) {
              Alert.alert('错误', '请输入有效的数字');
              return;
            }
            try {
              const result = await awardService.giveAward(
                selectedChild.child_id,
                parseInt(minutes),
                '家长奖励'
              );
              Alert.alert('成功', `已为${selectedChild.name}发放${minutes}分钟游戏时间`);
              loadChildren();
            } catch (error) {
              Alert.alert('错误', '发放失败: ' + error.message);
            }
          },
        },
      ]
    );
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>家长控制面板</Text>
      
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>我的孩子</Text>
        {children.map((child) => (
          <TouchableOpacity
            key={child.child_id}
            style={[
              styles.childCard,
              selectedChild?.child_id === child.child_id && styles.selectedCard,
            ]}
            onPress={() => {
              setSelectedChild(child);
              loadStats(child.child_id);
            }}
          >
            <Text style={styles.childName}>{child.name}</Text>
            <Text style={styles.childInfo}>游戏积分: {child.game_balance} 分钟</Text>
          </TouchableOpacity>
        ))}
      </View>

      {selectedChild && stats && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>{selectedChild.name} - 数据统计</Text>
          <View style={styles.statsCard}>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>总练琴时间</Text>
              <Text style={styles.statValue}>{stats.total_minutes} 分钟</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>平均每日</Text>
              <Text style={styles.statValue}>{stats.average_daily} 分钟</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statLabel}>练琴天数</Text>
              <Text style={styles.statValue}>{stats.days_practiced} 天</Text>
            </View>
          </View>
        </View>
      )}

      <TouchableOpacity 
        style={styles.button}
        onPress={handleGiveAward}
        disabled={!selectedChild}
      >
        <Text style={styles.buttonText}>发放游戏时间 🎮</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
    color: '#333',
  },
  section: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#555',
  },
  childCard: {
    backgroundColor: 'white',
    padding: 15,
    borderRadius: 8,
    marginBottom: 10,
    borderLeftWidth: 4,
    borderLeftColor: '#ccc',
  },
  selectedCard: {
    borderLeftColor: '#007AFF',
    backgroundColor: '#f0f4ff',
  },
  childName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  childInfo: {
    fontSize: 14,
    color: '#888',
    marginTop: 5,
  },
  statsCard: {
    backgroundColor: 'white',
    padding: 15,
    borderRadius: 8,
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  statItem: {
    alignItems: 'center',
  },
  statLabel: {
    fontSize: 12,
    color: '#888',
    marginBottom: 5,
  },
  statValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#007AFF',
  },
  button: {
    backgroundColor: '#007AFF',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 20,
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
