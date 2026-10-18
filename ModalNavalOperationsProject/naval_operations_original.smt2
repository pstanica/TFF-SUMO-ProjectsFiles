; Exact translation of the active naval_operations_scenario.tff input.
; 46 axioms. No domain closure or priority constraints have been added.
; A theorem test asserts axioms AND the negation of the active conjecture.
; The active conjecture is NOT unresolvable_conflict(w0).
; Thus SAT here is a counterexample to the claimed absence of unresolved conflict.
; Timeout is 600000 milliseconds = 600 seconds per check.
(set-logic UF)
(set-option :produce-models true)
(set-option :timeout 600000)
(declare-sort world 0)
(declare-sort agent 0)
(declare-sort authority 0)
(declare-sort prop 0)
(declare-fun k_accessible (agent world world) Bool)
(declare-fun b_accessible (agent world world) Bool)
(declare-fun o_accessible (authority world world) Bool)
(declare-fun auth_priority (authority authority world) Bool)
(declare-fun active (authority world) Bool)
(declare-fun holds (prop world) Bool)
(declare-fun knows (agent prop world) Bool)
(declare-fun believes (agent prop world) Bool)
(declare-fun obligatory (authority prop world) Bool)
(declare-fun commander () agent)
(declare-fun unclos () authority)
(declare-fun roe () authority)
(declare-fun nsd () authority)
(declare-fun issue_warning () prop)
(declare-fun immediate_action () prop)
(declare-fun protect_asset () prop)
(declare-fun threat_detected () prop)
(declare-fun in_territorial_waters () prop)
(declare-fun strategic_asset_nearby () prop)
(declare-fun w0 () world)
(declare-fun w1 () world)
(declare-fun w2 () world)
(declare-fun conflict (prop prop world) Bool)
(declare-fun effective_obligation (prop world) Bool)
(declare-fun unresolvable_conflict (world) Bool)

; knows_def
(assert (! (forall ((A agent) (P prop) (W world)) (= (knows A P W) (forall ((W2 world)) (=> (k_accessible A W W2) (holds P W2))))) :named knows_def))

; believes_def
(assert (! (forall ((A agent) (P prop) (W world)) (= (believes A P W) (forall ((W2 world)) (=> (b_accessible A W W2) (holds P W2))))) :named believes_def))

; obligatory_def
(assert (! (forall ((Auth authority) (P prop) (W world)) (= (obligatory Auth P W) (forall ((W2 world)) (=> (o_accessible Auth W W2) (holds P W2))))) :named obligatory_def))

; threat_at_w0
(assert (! (holds threat_detected w0) :named threat_at_w0))

; asset_at_w0
(assert (! (holds strategic_asset_nearby w0) :named asset_at_w0))

; territorial_at_w0
(assert (! (holds in_territorial_waters w0) :named territorial_at_w0))

; issue_warning_requires_territorial
(assert (! (forall ((W world)) (=> (holds issue_warning W) (holds in_territorial_waters W))) :named issue_warning_requires_territorial))

; commander_knows_threat
(assert (! (forall ((W world)) (=> (k_accessible commander w0 W) (holds threat_detected W))) :named commander_knows_threat))

; commander_knows_asset
(assert (! (forall ((W world)) (=> (k_accessible commander w0 W) (holds strategic_asset_nearby W))) :named commander_knows_asset))

; commander_knows_threat_at_w0
(assert (! (knows commander threat_detected w0) :named commander_knows_threat_at_w0))

; commander_knows_asset_at_w0
(assert (! (knows commander strategic_asset_nearby w0) :named commander_knows_asset_at_w0))

; commander_believes_territorial
(assert (! (exists ((W world)) (and (b_accessible commander w0 W) (holds in_territorial_waters W))) :named commander_believes_territorial))

; commander_uncertain_territorial
(assert (! (exists ((W world)) (and (b_accessible commander w0 W) (not (holds in_territorial_waters W)))) :named commander_uncertain_territorial))

; belief_in_knowledge
(assert (! (forall ((W world)) (=> (b_accessible commander w0 W) (k_accessible commander w0 W))) :named belief_in_knowledge))

; unclos_activation
(assert (! (forall ((W world)) (=> (holds in_territorial_waters W) (active unclos W))) :named unclos_activation))

; roe_activation
(assert (! (forall ((W world)) (active roe W)) :named roe_activation))

; nsd_activation
(assert (! (forall ((W world)) (=> (holds strategic_asset_nearby W) (active nsd W))) :named nsd_activation))

; unclos_active_at_w0
(assert (! (active unclos w0) :named unclos_active_at_w0))

; roe_active_at_w0
(assert (! (active roe w0) :named roe_active_at_w0))

; nsd_active_at_w0
(assert (! (active nsd w0) :named nsd_active_at_w0))

; unclos_obligation
(assert (! (forall ((W world)) (=> (active unclos W) (obligatory unclos issue_warning W))) :named unclos_obligation))

; roe_obligation
(assert (! (forall ((W world)) (=> (and (active roe W) (holds threat_detected W)) (obligatory roe immediate_action W))) :named roe_obligation))

; nsd_obligation
(assert (! (forall ((W world)) (=> (active nsd W) (obligatory nsd protect_asset W))) :named nsd_obligation))

; unclos_obligates_warning_at_w0
(assert (! (obligatory unclos issue_warning w0) :named unclos_obligates_warning_at_w0))

; roe_obligates_action_at_w0
(assert (! (obligatory roe immediate_action w0) :named roe_obligates_action_at_w0))

; nsd_obligates_protection_at_w0
(assert (! (obligatory nsd protect_asset w0) :named nsd_obligates_protection_at_w0))

; action_conflicts_warning
(assert (! (forall ((W world)) (=> (holds immediate_action W) (not (holds issue_warning W)))) :named action_conflicts_warning))

; warning_conflicts_action
(assert (! (forall ((W world)) (=> (holds issue_warning W) (not (holds immediate_action W)))) :named warning_conflicts_action))

; roe_priority_over_unclos
(assert (! (auth_priority unclos roe w0) :named roe_priority_over_unclos))

; nsd_roe_incomparable_1
(assert (! (not (auth_priority nsd roe w0)) :named nsd_roe_incomparable_1))

; nsd_roe_incomparable_2
(assert (! (not (auth_priority roe nsd w0)) :named nsd_roe_incomparable_2))

; nsd_priority_over_unclos
(assert (! (auth_priority unclos nsd w0) :named nsd_priority_over_unclos))

; authority_consistency
(assert (! (forall ((Auth authority) (P prop) (W world)) (not (and (obligatory Auth P W) (exists ((W2 world)) (and (o_accessible Auth W W2) (not (holds P W2))))))) :named authority_consistency))

; knowledge_reflexive
(assert (! (forall ((A agent) (W world)) (k_accessible A W W)) :named knowledge_reflexive))

; knowledge_symmetric
(assert (! (forall ((A agent) (W1 world) (W2 world)) (=> (k_accessible A W1 W2) (k_accessible A W2 W1))) :named knowledge_symmetric))

; knowledge_transitive
(assert (! (forall ((A agent) (W1 world) (W2 world) (W3 world)) (=> (and (k_accessible A W1 W2) (k_accessible A W2 W3)) (k_accessible A W1 W3))) :named knowledge_transitive))

; belief_serial
(assert (! (forall ((A agent) (W world)) (exists ((W2 world)) (b_accessible A W W2))) :named belief_serial))

; belief_transitive
(assert (! (forall ((A agent) (W1 world) (W2 world) (W3 world)) (=> (and (b_accessible A W1 W2) (b_accessible A W2 W3)) (b_accessible A W1 W3))) :named belief_transitive))

; belief_euclidean
(assert (! (forall ((A agent) (W1 world) (W2 world) (W3 world)) (=> (and (b_accessible A W1 W2) (b_accessible A W1 W3)) (b_accessible A W2 W3))) :named belief_euclidean))

; obligation_serial
(assert (! (forall ((Auth authority) (W world)) (=> (active Auth W) (exists ((W2 world)) (o_accessible Auth W W2)))) :named obligation_serial))

; conflict_def
(assert (! (forall ((P1 prop) (P2 prop) (W world)) (= (conflict P1 P2 W) (exists ((Auth1 authority) (Auth2 authority)) (and (and (and (not (= Auth1 Auth2)) (obligatory Auth1 P1 W)) (obligatory Auth2 P2 W)) (forall ((W2 world)) (=> (holds P1 W2) (not (holds P2 W2)))))))) :named conflict_def))

; nsd_roe_compatible
(assert (! (exists ((W world)) (and (holds immediate_action W) (holds protect_asset W))) :named nsd_roe_compatible))

; priority_resolution
(assert (! (forall ((P1 prop) (P2 prop) (Auth1 authority) (Auth2 authority) (W world)) (=> (and (and (and (obligatory Auth1 P1 W) (obligatory Auth2 P2 W)) (auth_priority Auth1 Auth2 W)) (forall ((W2 world)) (=> (holds P1 W2) (not (holds P2 W2))))) (effective_obligation P2 W))) :named priority_resolution))

; effective_obligation_immediate_action
(assert (! (effective_obligation immediate_action w0) :named effective_obligation_immediate_action))

; unresolvable_def
(assert (! (forall ((W world)) (= (unresolvable_conflict W) (exists ((P1 prop) (P2 prop) (Auth1 authority) (Auth2 authority)) (and (and (and (and (conflict P1 P2 W) (obligatory Auth1 P1 W)) (obligatory Auth2 P2 W)) (not (auth_priority Auth1 Auth2 W))) (not (auth_priority Auth2 Auth1 W)))))) :named unresolvable_def))

; prop_exhaustive
(assert (! (forall ((P prop)) (or (or (or (or (or (= P issue_warning) (= P immediate_action)) (= P protect_asset)) (= P threat_detected)) (= P in_territorial_waters)) (= P strategic_asset_nearby))) :named prop_exhaustive))

; Negation of active conjecture query_no_unresolvable_conflict
(assert (! (not (not (unresolvable_conflict w0))) :named negated_conjecture))
(check-sat)
(get-info :all-statistics)
