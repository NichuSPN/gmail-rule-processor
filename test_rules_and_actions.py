import unittest
from utils.rules_and_actions import (
    validate_condition,
    get_sql_condition,
    process_rule,
    process_action,
    action_locations,
    action_categories
)


class TestRulesAndActions(unittest.TestCase):
    
    def test_validate_condition_valid(self):
        # Test valid text conditions
        validate_condition({"field": "from_address", "operator": "is", "value": "test@example.com"})
        validate_condition({"field": "subject", "operator": "contains", "value": "hello"})
        validate_condition({"field": "body", "operator": "not_contains", "value": "spam"})
        
        # Test valid datetime conditions
        validate_condition({"field": "received_at", "operator": "greater_than", "value": "7 days"})
        validate_condition({"field": "received_at", "operator": "less_than", "value": "1 month"})

    def test_validate_condition_invalid_field(self):
        with self.assertRaises(ValueError):
            validate_condition({"field": "invalid_field", "operator": "is", "value": "test"})
    
    def test_validate_condition_invalid_operator(self):
        with self.assertRaises(ValueError):
            validate_condition({"field": "from_address", "operator": "invalid_op", "value": "test"})
        
        # Text field with datetime operator
        with self.assertRaises(ValueError):
            validate_condition({"field": "from_address", "operator": "greater_than", "value": "test"})
    
    def test_validate_condition_invalid_value(self):
        # Invalid datetime format
        with self.assertRaises(ValueError):
            validate_condition({"field": "received_at", "operator": "greater_than", "value": "invalid"})
    
    def test_get_sql_condition(self):
        # Test contains operator
        self.assertEqual(
            get_sql_condition({"field": "from_address", "operator": "contains", "value": "example"}),
            "from_address ilike '%example%'"
        )
        
        # Test is operator
        self.assertEqual(
            get_sql_condition({"field": "subject", "operator": "is", "value": "Hello"}),
            "subject = 'Hello'"
        )
        
        # Test greater_than operator
        self.assertEqual(
            get_sql_condition({"field": "received_at", "operator": "greater_than", "value": "7 days"}),
            "received_at > now() - interval '7 days'"
        )
    
    def test_process_rule_single_condition(self):
        rule = {
            "type": "condition",
            "field": "from_address",
            "operator": "contains",
            "value": "example.com"
        }
        
        self.assertEqual(
            process_rule(rule),
            "from_address ilike '%example.com%'"
        )
    
    def test_process_rule_all_predicate(self):
        rule = {
            "type": "rule",
            "predicate": "all",
            "rules": [
                {
                    "type": "condition",
                    "field": "from_address",
                    "operator": "contains",
                    "value": "example.com"
                },
                {
                    "type": "condition",
                    "field": "subject",
                    "operator": "contains",
                    "value": "important"
                }
            ]
        }
        
        self.assertEqual(
            process_rule(rule),
            "(from_address ilike '%example.com%' and subject ilike '%important%')"
        )
    
    def test_process_rule_any_predicate(self):
        rule = {
            "type": "rule",
            "predicate": "any",
            "rules": [
                {
                    "type": "condition",
                    "field": "from_address",
                    "operator": "contains",
                    "value": "example.com"
                },
                {
                    "type": "condition",
                    "field": "subject",
                    "operator": "contains",
                    "value": "important"
                }
            ]
        }
        
        self.assertEqual(
            process_rule(rule),
            "(from_address ilike '%example.com%' or subject ilike '%important%')"
        )
    
    def test_process_rule_nested(self):
        rule = {
            "type": "rule",
            "predicate": "all",
            "rules": [
                {
                    "type": "condition",
                    "field": "from_address",
                    "operator": "contains",
                    "value": "example.com"
                },
                {
                    "type": "rule",
                    "predicate": "any",
                    "rules": [
                        {
                            "type": "condition",
                            "field": "subject",
                            "operator": "contains",
                            "value": "important"
                        },
                        {
                            "type": "condition",
                            "field": "body",
                            "operator": "contains",
                            "value": "urgent"
                        }
                    ]
                }
            ]
        }
        
        self.assertEqual(
            process_rule(rule),
            "(from_address ilike '%example.com%' and (subject ilike '%important%' or body ilike '%urgent%'))"
        )
    
    def test_process_rule_empty(self):
        rule = {
            "type": "rule",
            "predicate": "all",
            "rules": []
        }
        
        self.assertIsNone(process_rule(rule))
    
    def test_process_action_basic(self):
        action = {
            "unread": True,
            "starred": True
        }
        
        add_labels, remove_labels = process_action(action)
        self.assertIn("UNREAD", add_labels)
        self.assertIn("STARRED", add_labels)
        self.assertEqual(len(remove_labels), 0)
    
    def test_process_action_unread_false(self):
        action = {
            "unread": False
        }
        
        add_labels, remove_labels = process_action(action)
        self.assertEqual(len(add_labels), 0)
        self.assertIn("UNREAD", remove_labels)
    
    def test_process_action_location(self):
        action = {
            "location": "INBOX"
        }
        
        add_labels, remove_labels = process_action(action)
        self.assertIn("INBOX", add_labels)
        # Should remove other locations
        self.assertIn("SPAM", remove_labels)
        self.assertIn("TRASH", remove_labels)
    
    def test_process_action_invalid_location(self):
        action = {
            "location": "INVALID_LOCATION"
        }
        
        with self.assertRaises(ValueError):
            process_action(action)
    
    def test_process_action_category(self):
        action = {
            "category": "CATEGORY_PERSONAL"
        }
        
        add_labels, remove_labels = process_action(action)
        self.assertIn("CATEGORY_PERSONAL", add_labels)
        # Should remove other categories
        self.assertIn("CATEGORY_SOCIAL", remove_labels)
        self.assertIn("CATEGORY_PROMOTIONS", remove_labels)
    
    def test_process_action_invalid_category(self):
        action = {
            "category": "INVALID_CATEGORY"
        }
        
        with self.assertRaises(ValueError):
            process_action(action)
    
    def test_process_action_complete(self):
        action = {
            "unread": True,
            "starred": True,
            "important": True,
            "location": "INBOX",
            "category": "CATEGORY_PERSONAL"
        }
        
        add_labels, remove_labels = process_action(action)
        
        # Check added labels
        self.assertIn("UNREAD", add_labels)
        self.assertIn("STARRED", add_labels)
        self.assertIn("IMPORTANT", add_labels)
        self.assertIn("INBOX", add_labels)
        self.assertIn("CATEGORY_PERSONAL", add_labels)
        
        # Check removed labels
        self.assertIn("SPAM", remove_labels)
        self.assertIn("TRASH", remove_labels)
        for category in action_categories:
            if category != "CATEGORY_PERSONAL":
                self.assertIn(category, remove_labels)


if __name__ == "__main__":
    unittest.main() 