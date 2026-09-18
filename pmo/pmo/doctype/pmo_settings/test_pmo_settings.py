# Copyright (c) 2026, PMO CSB and contributors
# For license information, please see license.txt

import frappe
from frappe.permissions import has_permission
from frappe.tests import IntegrationTestCase

BUSINESS_DOCTYPES = ("Action Item", "Challenge", "Watch Item", "Progress Update", "Submission")
MASTER_DOCTYPES = ("Unit", "Entity")


def user_holding(role):
	user = frappe.get_doc(
		{
			"doctype": "User",
			"email": f"{frappe.generate_hash(length=10)}@pmo.test",
			"first_name": role,
			"send_welcome_email": 0,
			"roles": [{"role": role}],
		}
	).insert()
	return user.name


class TestPMOSettings(IntegrationTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.pmo_manager = user_holding("PMO Manager")
		cls.project_manager = user_holding("Project Manager")
		cls.project_specialist = user_holding("Project Specialist")

	def allowed(self, doctype, ptype, user):
		return has_permission(doctype, ptype, user=user, print_logs=False)

	def test_pmo_manager_writes_pmo_settings_while_project_roles_only_read_it(self):
		self.assertTrue(self.allowed("PMO Settings", "write", self.pmo_manager))

		for user in (self.project_manager, self.project_specialist):
			self.assertTrue(self.allowed("PMO Settings", "read", user), msg=user)
			self.assertFalse(self.allowed("PMO Settings", "write", user), msg=user)

	def test_project_roles_write_business_records_but_only_read_masters(self):
		for user in (self.project_manager, self.project_specialist):
			for doctype in BUSINESS_DOCTYPES:
				self.assertTrue(self.allowed(doctype, "write", user), msg=f"{user} {doctype}")

			for doctype in MASTER_DOCTYPES:
				self.assertTrue(self.allowed(doctype, "read", user), msg=f"{user} {doctype}")
				self.assertFalse(self.allowed(doctype, "write", user), msg=f"{user} {doctype}")

	def test_only_pmo_manager_deletes_a_business_record(self):
		for doctype in BUSINESS_DOCTYPES:
			self.assertTrue(self.allowed(doctype, "delete", self.pmo_manager), msg=doctype)

			for user in (self.project_manager, self.project_specialist):
				self.assertFalse(self.allowed(doctype, "delete", user), msg=f"{user} {doctype}")
