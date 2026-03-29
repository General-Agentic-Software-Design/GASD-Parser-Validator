#ifndef RAFT_H
#define RAFT_H

#include <stdbool.h>
#include <stdint.h>

#define MAX_LOG_ENTRIES 100

/**
 * TYPE NodeState: Enum(FOLLOWER, CANDIDATE, LEADER)
 */
typedef enum { FOLLOWER, CANDIDATE, LEADER } NodeState;

/**
 * TYPE LogEntry
 */
typedef struct {
  int term;
  char command[256];
  int index; // @unique
} LogEntry;

/**
 * TYPE Message
 */
typedef enum { REQUEST_VOTE, APPEND_ENTRIES, HEARTBEAT } MessageType;

typedef struct {
  MessageType type;
  int term;
  uint8_t sender_id[16];
} Message;

typedef struct {
  int success;
  int term;
} Response;

typedef struct {
  int current_term;
  NodeState state;
  int votes_received;
  int cluster_size;
  int voted_for; // -1 if none
  LogEntry log[MAX_LOG_ENTRIES];
  int log_count;
} RaftNode;

/**
 * STRATEGY leader_election
 */
bool raft_check_election_result(RaftNode *node);

/**
 * FLOW handle_message(node, msg)
 */
Response raft_handle_message(RaftNode *node, Message msg);

/**
 * FLOW start_election(node)
 */
void raft_start_election(RaftNode *node);

/**
 * Helper to get state name
 */
const char *raft_get_state_name(NodeState state);

#endif // RAFT_H
