#include "raft.h"
#include <stdio.h>
#include <string.h>

// Mock ACHIEVE functions
void achieve_update_local_term(RaftNode *node, int term) {
  printf("[ACHIEVE] Update Local Term: %d -> %d\n", node->current_term, term);
  node->current_term = term;
  node->voted_for = -1;
}

void achieve_step_down_to_follower(RaftNode *node) {
  if (node->state != FOLLOWER) {
    printf("[ACHIEVE] Step Down to Follower\n");
    node->state = FOLLOWER;
  }
}

void achieve_reset_election_timer() {
  printf("[ACHIEVE] Reset Election Timer\n");
}

void achieve_replicate_log(RaftNode *node) {
  printf("[ACHIEVE] Replicate Log (entries: %d)\n", node->log_count);
}

void achieve_increment_term(RaftNode *node) {
  node->current_term++;
  printf("[ACHIEVE] Increment Term to %d\n", node->current_term);
}

void achieve_become_candidate(RaftNode *node) {
  printf("[ACHIEVE] Become Candidate\n");
  node->state = CANDIDATE;
}

void achieve_vote_for_self(RaftNode *node) {
  printf("[ACHIEVE] Vote for Self\n");
  node->voted_for = 1; // Assuming self ID is 1
  node->votes_received = 1;
}

void achieve_broadcast_request_vote() {
  printf("[ACHIEVE] Broadcast RequestVote\n");
}

void achieve_become_leader(RaftNode *node) {
  printf("[ACHIEVE] Become Leader\n");
  node->state = LEADER;
}

void achieve_start_heartbeat() { printf("[ACHIEVE] Start Heartbeat\n"); }

const char *raft_get_state_name(NodeState state) {
  switch (state) {
  case FOLLOWER:
    return "FOLLOWER";
  case CANDIDATE:
    return "CANDIDATE";
  case LEADER:
    return "LEADER";
  default:
    return "UNKNOWN";
  }
}

bool raft_check_election_result(RaftNode *node) {
  if (node->state != CANDIDATE)
    return false;
  return node->votes_received > (node->cluster_size / 2);
}

Response raft_handle_message(RaftNode *node, Message msg) {
  Response resp = {.success = 0, .term = node->current_term};

  // 1. IF msg.term > node.current_term:
  if (msg.term > node->current_term) {
    achieve_update_local_term(node, msg.term);
    achieve_step_down_to_follower(node);
    resp.term = node->current_term;
  }

  // 2. MATCH msg.type:
  switch (msg.type) {
  case REQUEST_VOTE:
    // ACHIEVE "Handle Vote Request"
    if (msg.term < node->current_term) {
      resp.success = 0;
    } else if (node->voted_for == -1) {
      printf("[ACHIEVE] Grant Vote (term=%d)\n", msg.term);
      node->voted_for = 1; // Mocking sender_id
      resp.success = 1;
    } else {
      resp.success = 0;
    }
    break;

  case APPEND_ENTRIES:
    // ENSURE msg.term >= node.current_term
    if (msg.term < node->current_term) {
      resp.success = 0;
      return resp;
    }
    achieve_replicate_log(node);
    achieve_step_down_to_follower(node);
    resp.success = 1;
    break;

  case HEARTBEAT:
    if (msg.term >= node->current_term) {
      achieve_reset_election_timer();
      achieve_step_down_to_follower(node);
      resp.success = 1;
    }
    break;

  default:
    printf("LOG Unknown message type ignored\n");
    break;
  }

  return resp;
}

void raft_start_election(RaftNode *node) {
  if (node->state != FOLLOWER) {
    printf("CANNOT START ELECTION: Node is already %s\n",
           raft_get_state_name(node->state));
    return;
  }

  achieve_increment_term(node);
  achieve_become_candidate(node);
  achieve_vote_for_self(node);
  achieve_broadcast_request_vote();

  printf("Waiting for votes... (simulated majority)\n");
  node->votes_received = (node->cluster_size / 2) + 1;

  if (raft_check_election_result(node)) {
    achieve_become_leader(node);
    achieve_start_heartbeat();
  }
}
