import apiClient from '../api/api';
import type { UserRead, UserUpdate } from '../types/auth';

export const getProfile = async () => {
    const response = await apiClient.get<UserRead>('/profile/');
    return response.data;
};

export const updateProfile = async (data: UserUpdate) => {
    const response = await apiClient.put<UserRead>('/profile/', data);
    return response.data;
};

export const uploadProfileImage = async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post<{ url: string }>('/profile/upload-image', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};
