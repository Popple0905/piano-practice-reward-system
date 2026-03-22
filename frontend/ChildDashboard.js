import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, TextInput, Alert } from 'react-native';
import { practiceService, awardService } from '../services';

export function ChildDashboard({ route }) {
  const [childId] = useState(route.params?.childId);
  const [childName] = useState(route.params?.childName);
  const [practiceMinutes, setPracticeMinutes] = useState('');
  const [notes, setNotes] = useState('');
  const [balance, setBalance] = useState(0);
  const [todayRecords, setTodayRecords] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const balanceData = await awardService.getBalance(childId);
      setBalance(balanceData.game_balance);
      
      const today = new Date().toISOString().split('T')[0];
      const recordsData = await practiceService.getRecords(childId, today, today);
      setTodayRecords(recordsData.records || []);
    } catch (error) {
      console.error('加载数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddRecord = async () => {
    if (!practiceMinutes || isNaN(practiceMinutes)) {
      Alert.alert('错误', '请输入有效的练琴时间');
      return;
    }

    try {
      const today = new Date().toISOString().split('T')[0];
      await practiceService.addRecord(today, parseInt(practiceMinutes), notes);
      Alert.alert('成功', '练琴记录已保存！');
      setPracticeMinutes('');
      setNotes('');
      loadData();
    } catch (error) {
      Alert.alert('错误', '保存失败: ' + error.message);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>🎹 {childName}</Text>

      {/* 游戏积分卡片 */}
      <View style={styles.balanceCard}>
        <Text style={styles.balanceLabel}>我的游戏积分</Text>
        <Text style={styles.balanceValue}>{balance}</Text>
        <Text style={styles.balanceUnit}>分钟</Text>
      </View>

      {/* 今日练琴记录 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>📝 今日练琴</Text>
        {todayRecords.length > 0 ? (
          todayRecords.map((record) => (
            <View key={record.id} style={styles.recordCard}>
              <Text style={styles.recordTime}>{record.practice_minutes} 分钟</Text>
              {record.notes && <Text style={styles.recordNotes}>{record.notes}</Text>}
            </View>
          ))
        ) : (
          <Text style={styles.noData}>今天还没有练琴记录</Text>
        )}
      </View>

      {/* 添加练琴记录 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>➕ 添加今日练琴</Text>
        <View style={styles.inputGroup}>
          <TextInput
            style={styles.input}
            placeholder="练琴时间（分钟）"
            keyboardType="numeric"
            value={practiceMinutes}
            onChangeText={setPracticeMinutes}
          />
          <TextInput
            style={[styles.input, styles.notesInput]}
            placeholder="备注（今天练了什么？）"
            value={notes}
            onChangeText={setNotes}
            multiline
          />
          <TouchableOpacity 
            style={styles.submitButton}
            onPress={handleAddRecord}
            disabled={!practiceMinutes}
          >
            <Text style={styles.submitButtonText}>保存记录 ✅</Text>
          </TouchableOpacity>
        </View>
      </View>
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
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 20,
    color: '#333',
  },
  balanceCard: {
    backgroundColor: '#FFD700',
    padding: 20,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 20,
    elevation: 5,
  },
  balanceLabel: {
    fontSize: 14,
    color: '#333',
  },
  balanceValue: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#333',
    marginVertical: 10,
  },
  balanceUnit: {
    fontSize: 14,
    color: '#555',
  },
  section: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#555',
  },
  recordCard: {
    backgroundColor: 'white',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
  },
  recordTime: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#007AFF',
  },
  recordNotes: {
    fontSize: 14,
    color: '#888',
    marginTop: 5,
  },
  noData: {
    color: '#ccc',
    textAlign: 'center',
    padding: 20,
  },
  inputGroup: {
    backgroundColor: 'white',
    padding: 15,
    borderRadius: 8,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    padding: 12,
    borderRadius: 8,
    marginBottom: 10,
    fontSize: 14,
  },
  notesInput: {
    height: 80,
    textAlignVertical: 'top',
  },
  submitButton: {
    backgroundColor: '#4CAF50',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
  },
  submitButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
