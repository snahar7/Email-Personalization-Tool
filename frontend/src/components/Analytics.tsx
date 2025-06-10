import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Grid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  useToast,
  Select,
  Card,
  CardBody,
} from '@chakra-ui/react';
import { api } from '../services/api';

interface EngagementMetrics {
  total_sent: number;
  total_opened: number;
  total_clicked: number;
  total_replied: number;
  average_engagement_score: number;
  best_performing_template: string | null;
  best_sending_time: string | null;
}

const Analytics = () => {
  const [metrics, setMetrics] = useState<EngagementMetrics | null>(null);
  const [timeRange, setTimeRange] = useState('30');
  const toast = useToast();

  useEffect(() => {
    fetchMetrics();
  }, [timeRange]);

  const fetchMetrics = async () => {
    try {
      const response = await api.get(`/engagements/metrics/?days=${timeRange}`);
      setMetrics(response.data);
    } catch (error) {
      toast({
        title: 'Error fetching metrics',
        status: 'error',
        duration: 3000,
      });
    }
  };

  const calculatePercentage = (value: number, total: number) => {
    if (total === 0) return 0;
    return ((value / total) * 100).toFixed(1);
  };

  return (
    <VStack spacing={6} align="stretch">
      <HStack justify="space-between">
        <Text fontSize="2xl" fontWeight="bold">
          Analytics Dashboard
        </Text>
        <Select
          value={timeRange}
          onChange={(e) => setTimeRange(e.target.value)}
          width="200px"
        >
          <option value="7">Last 7 days</option>
          <option value="30">Last 30 days</option>
          <option value="90">Last 90 days</option>
          <option value="365">Last year</option>
        </Select>
      </HStack>

      <Grid templateColumns="repeat(4, 1fr)" gap={6}>
        <Card>
          <CardBody>
            <Stat>
              <StatLabel>Total Emails Sent</StatLabel>
              <StatNumber>{metrics?.total_sent || 0}</StatNumber>
              <StatHelpText>
                <StatArrow type="increase" />
                {calculatePercentage(metrics?.total_opened || 0, metrics?.total_sent || 1)}% open rate
              </StatHelpText>
            </Stat>
          </CardBody>
        </Card>

        <Card>
          <CardBody>
            <Stat>
              <StatLabel>Open Rate</StatLabel>
              <StatNumber>
                {calculatePercentage(metrics?.total_opened || 0, metrics?.total_sent || 1)}%
              </StatNumber>
              <StatHelpText>
                <StatArrow type="increase" />
                {metrics?.total_opened || 0} opens
              </StatHelpText>
            </Stat>
          </CardBody>
        </Card>

        <Card>
          <CardBody>
            <Stat>
              <StatLabel>Click Rate</StatLabel>
              <StatNumber>
                {calculatePercentage(metrics?.total_clicked || 0, metrics?.total_sent || 1)}%
              </StatNumber>
              <StatHelpText>
                <StatArrow type="increase" />
                {metrics?.total_clicked || 0} clicks
              </StatHelpText>
            </Stat>
          </CardBody>
        </Card>

        <Card>
          <CardBody>
            <Stat>
              <StatLabel>Reply Rate</StatLabel>
              <StatNumber>
                {calculatePercentage(metrics?.total_replied || 0, metrics?.total_sent || 1)}%
              </StatNumber>
              <StatHelpText>
                <StatArrow type="increase" />
                {metrics?.total_replied || 0} replies
              </StatHelpText>
            </Stat>
          </CardBody>
        </Card>
      </Grid>

      <Grid templateColumns="repeat(2, 1fr)" gap={6}>
        <Card>
          <CardBody>
            <VStack align="stretch" spacing={4}>
              <Text fontSize="lg" fontWeight="bold">
                Best Performing Template
              </Text>
              <Text>
                {metrics?.best_performing_template || 'No data available'}
              </Text>
            </VStack>
          </CardBody>
        </Card>

        <Card>
          <CardBody>
            <VStack align="stretch" spacing={4}>
              <Text fontSize="lg" fontWeight="bold">
                Best Sending Time
              </Text>
              <Text>
                {metrics?.best_sending_time || 'No data available'}
              </Text>
            </VStack>
          </CardBody>
        </Card>
      </Grid>

      <Card>
        <CardBody>
          <VStack align="stretch" spacing={4}>
            <Text fontSize="lg" fontWeight="bold">
              Average Engagement Score
            </Text>
            <Text fontSize="3xl" fontWeight="bold" color="cyan.500">
              {metrics?.average_engagement_score.toFixed(1) || 0}
            </Text>
            <Text color="gray.500">
              Based on opens, clicks, and replies
            </Text>
          </VStack>
        </CardBody>
      </Card>
    </VStack>
  );
};

export default Analytics; 