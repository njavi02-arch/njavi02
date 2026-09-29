import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  SafeAreaView,
  TouchableOpacity,
  Image,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { useRealtimeSocket } from '../hooks/useRealtimeSocket';

interface Profile {
  id: string;
  username: string;
  firstName: string;
  profilePhoto?: string;
  age: number;
  distance: number;
  compatibilityScore: number;
  hashtags: string[];
  anonymousMode: boolean;
}

export function DiscoveryScreen() {
  const { likeProfile, passProfile, superlikeProfile } = useRealtimeSocket();
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load discovery profiles (mock data for now)
    fetchProfiles();
  }, []);

  const fetchProfiles = async () => {
    try {
      setLoading(true);
      // Mock profiles for testing
      const mockProfiles: Profile[] = [
        {
          id: '1',
          username: 'users_anonymous_123',
          firstName: '👤 Anónimo',
          age: 26,
          distance: 2.5,
          compatibilityScore: 92,
          hashtags: ['adventure', 'travel'],
          anonymousMode: true,
        },
        {
          id: '2',
          username: 'sarah_92',
          firstName: 'Sarah',
          age: 28,
          distance: 1.2,
          compatibilityScore: 87,
          hashtags: ['music', 'art'],
          anonymousMode: false,
        },
        {
          id: '3',
          username: 'emma_private',
          firstName: '👤 Privada',
          age: 25,
          distance: 3.8,
          compatibilityScore: 85,
          hashtags: ['fitness', 'wellness'],
          anonymousMode: true,
        },
      ];
      setProfiles(mockProfiles);
    } catch (error) {
      console.error('Error fetching profiles:', error);
      Alert.alert('Error', 'Failed to load profiles');
    } finally {
      setLoading(false);
    }
  };

  const handleLike = () => {
    const profile = profiles[currentIndex];
    likeProfile(profile.id);
    nextProfile();
  };

  const handlePass = () => {
    passProfile(profiles[currentIndex].id);
    nextProfile();
  };

  const handleSuperLike = () => {
    const profile = profiles[currentIndex];
    superlikeProfile(profile.id);
    nextProfile();
  };

  const nextProfile = () => {
    if (currentIndex < profiles.length - 1) {
      setCurrentIndex(currentIndex + 1);
    } else {
      Alert.alert('No more profiles', 'Come back later for more matches!');
      setCurrentIndex(0);
    }
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <ActivityIndicator size="large" color="#667eea" />
      </SafeAreaView>
    );
  }

  if (profiles.length === 0) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.emptyState}>
          <Text style={styles.emptyTitle}>No profiles available</Text>
          <TouchableOpacity
            style={styles.refreshButton}
            onPress={() => fetchProfiles()}
          >
            <Text style={styles.refreshButtonText}>Refresh</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  const currentProfile = profiles[currentIndex];

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>🔥 Descubrimiento</Text>
          <Text style={styles.headerSubtitle}>
            {currentIndex + 1} de {profiles.length} perfiles
          </Text>
        </View>

        {/* Profile Card */}
        <View style={styles.profileCard}>
          {/* Anonymous Badge */}
          {currentProfile.anonymousMode && (
            <View style={styles.anonymousBadge}>
              <Text style={styles.anonymousBadgeText}>👤 Anónimo</Text>
            </View>
          )}

          {/* Photo Placeholder */}
          <View style={styles.photoContainer}>
            {currentProfile.profilePhoto ? (
              <Image
                source={{ uri: currentProfile.profilePhoto }}
                style={styles.photo}
              />
            ) : (
              <View style={styles.photoPlaceholder}>
                <Text style={styles.photoPlaceholderText}>📸</Text>
              </View>
            )}
          </View>

          {/* Profile Info */}
          <View style={styles.profileInfo}>
            <View style={styles.nameRow}>
              <Text style={styles.profileName}>
                {currentProfile.firstName}, {currentProfile.age}
              </Text>
              <View style={styles.scoreContainer}>
                <Text style={styles.scoreText}>
                  {currentProfile.compatibilityScore}%
                </Text>
              </View>
            </View>

            <Text style={styles.distanceText}>
              📍 {currentProfile.distance} km away
            </Text>

            {/* Hashtags */}
            <View style={styles.hashtagsContainer}>
              {currentProfile.hashtags.map((tag, index) => (
                <View key={index} style={styles.hashtag}>
                  <Text style={styles.hashtagText}>#{tag}</Text>
                </View>
              ))}
            </View>

            {/* Privacy Info */}
            {currentProfile.anonymousMode && (
              <View style={styles.privacyInfo}>
                <Text style={styles.privacyText}>
                  ℹ️ Este usuario prefiere mantener su privacidad
                </Text>
              </View>
            )}
          </View>
        </View>

        {/* Action Buttons */}
        <View style={styles.actionButtons}>
          <TouchableOpacity
            style={[styles.actionButton, styles.passButton]}
            onPress={handlePass}
          >
            <Text style={styles.passButtonText}>👋 Pass</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.actionButton, styles.likeButton]}
            onPress={handleLike}
          >
            <Text style={styles.likeButtonText}>❤️ Like</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.actionButton, styles.superlikeButton]}
            onPress={handleSuperLike}
          >
            <Text style={styles.superlikeButtonText}>⭐ SuperLike</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: '#fff',
    paddingHorizontal: 16,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: '700',
    color: '#333',
  },
  headerSubtitle: {
    fontSize: 13,
    color: '#999',
    marginTop: 4,
  },
  profileCard: {
    backgroundColor: '#fff',
    marginHorizontal: 16,
    marginVertical: 16,
    borderRadius: 16,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  anonymousBadge: {
    position: 'absolute',
    top: 12,
    left: 12,
    backgroundColor: 'rgba(102, 126, 234, 0.9)',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
    zIndex: 10,
  },
  anonymousBadgeText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
  photoContainer: {
    width: '100%',
    height: 400,
    backgroundColor: '#f0f0f0',
  },
  photo: {
    width: '100%',
    height: '100%',
  },
  photoPlaceholder: {
    width: '100%',
    height: '100%',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#e8e8e8',
  },
  photoPlaceholderText: {
    fontSize: 80,
  },
  profileInfo: {
    padding: 16,
  },
  nameRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  profileName: {
    fontSize: 22,
    fontWeight: '700',
    color: '#333',
  },
  scoreContainer: {
    backgroundColor: '#667eea',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  scoreText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
  distanceText: {
    fontSize: 13,
    color: '#999',
    marginBottom: 12,
  },
  hashtagsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginBottom: 12,
  },
  hashtag: {
    backgroundColor: '#f0f0f0',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 8,
  },
  hashtagText: {
    fontSize: 12,
    color: '#667eea',
    fontWeight: '500',
  },
  privacyInfo: {
    backgroundColor: '#f8f9ff',
    padding: 10,
    borderRadius: 8,
    borderLeftWidth: 3,
    borderLeftColor: '#667eea',
  },
  privacyText: {
    fontSize: 12,
    color: '#666',
    fontWeight: '500',
  },
  actionButtons: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingHorizontal: 16,
    paddingVertical: 20,
    gap: 12,
  },
  actionButton: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  passButton: {
    backgroundColor: '#f0f0f0',
  },
  passButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
  },
  likeButton: {
    backgroundColor: '#ff6b6b',
  },
  likeButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#fff',
  },
  superlikeButton: {
    backgroundColor: '#ffd93d',
  },
  superlikeButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 100,
  },
  emptyTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#999',
    marginBottom: 16,
  },
  refreshButton: {
    backgroundColor: '#667eea',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 8,
  },
  refreshButtonText: {
    color: '#fff',
    fontWeight: '600',
  },
});
