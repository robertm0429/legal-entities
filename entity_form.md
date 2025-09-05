# Legal Entity Management (LEM) Form

## Core Entity Information

**DG Entity ID** (Auto-generated)

**Entity Name** ⭐ *Required*
Legal name of the entity. Must be unique in combination with Legal Entity Code.

**Sanitized Entity Name** (Auto-generated)

**Legal Entity Code** ⭐ *Required*
Short-hand code or identifier of the entity, often from the client's ERP system.

**Sanitized Entity Code** (Auto-generated)

**Entity Type** ⭐ *Required*
Select one:
- Branch – Non-legal entity extension (requires 1 owner only)
- Branch/Division – Non-legal entity extension
- Corporation – Any corporation variation (C Corp, S Corp, LLC)
- Disregarded – Legal entity ignored for tax purposes
- Entity Group – Dummy entity for consolidation/elimination
- Individual – A person
- Hybrid Partnership – Fiscally transparent domestically, corporation for foreign tax
- Partnership – Any partnership variation (GP, LP, LLP)
- Permanent Establishment – Fixed place of business
- Reverse Hybrid Corporation – Corporation domestically, fiscally transparent for foreign tax
- Trust – Fiduciary relationship for asset management

**DUNS Number**

## Dates & Status

**Effective Date**
Date the entity is legally formed or becomes effective.

**Termination Date**
Date the entity is sold off, liquidated, or otherwise terminated.

**Filing End Date**

**Fiscal Year End**
Month and Day of the entity's fiscal year end.

**Country of Incorporation**

**State of Incorporation**

**Date of Incorporation**

**Fund Status**
Identify as "Fund" or "Fund of Funds". In org chart's default Legal view, children of funds are hidden.

**Is Entity Displayed on Org Chart** ⭐ *Required*
Flag to hide the entity on the org chart.

## Location Information

**Jurisdiction** ⭐ *Required*
The domicile of the entity.

**Region** ⭐ *Required*

**State / Province / Locale**

**Street Address**

**City**

**County**

**Postal Code**

## Currency Information

**Local Currency** ⭐ *Required*
Default: US Dollar

**Functional Currency** ⭐ *Required*
Default: US Dollar

**Reporting Currency** ⭐ *Required*
Default: US Dollar

## Industry Classification

**Level One Industry**
Primary industry category.

**Level Two Industry**
Sub-category of primary industry.

**Level Three Industry**
Most specific industry classification.

## Additional Information

**Line of Business**

**Complexity**
Select one: Complex, Medium, Simple, Dormant

**Descriptor**
Select one: Holding Company, Operating Company, Cost Plus

**Client Purview**
Select one: Client entity, Joint Venture, External entity

**External Organization**
The other organization in Joint Venture or External entity.

**Comments**

---

## Filing Jurisdictions
The jurisdictions in which the entity has tax obligations. Required to utilize the entity in other DG Modules.

**Add Jurisdiction**
| Jurisdiction* | Region* | Filing Group | Tax Engine Code | Parent Tax Engine Code | Filing Hierarchy Level | VAT Id | Local Tax Number | Is Leader |
|---------------|---------|--------------|-----------------|------------------------|----------------------|--------|------------------|-----------|
|               |         |              |                 |                        |                      |        |                  |           |

---

## Entity Groups
Groupings of the entity for various purposes. The group flagged as primary will be the Legal Entity Group in other DG Modules.

**Add Entity Group**
| Name* | Is Primary |
|-------|------------|
|       |            |

---

## Applications
App-specific key-value pairs. Currently used for KDN, HighQ, and DMaaS.

### Digital Gateway Workflow
| Property | Value |
|----------|-------|
| Entity Type Name |  |

### Digital Gateway KDN
| Property | Value |
|----------|-------|
| Is Fictional Flag |  |

### Digital Gateway HighQ
| Property | Value |
|----------|-------|
| Diligence or Compute Share |  |
| Corporate Action Allowance |  |
| Date of Engagement |  |
| Renewal |  |
| Number of free client changes |  |

### Digital Gateway DMaaS
| Property | Value |
|----------|-------|
| Entity Official Name (local language) |  |
| ACN/ABRN (Australia) |  |
| ABN (Australia) |  |
| UEN (Singapore) |  |
| Business Registration Number (China) |  |
| Small Size/Micro Company (China) |  |
| Legal Representative (China) |  |
| Initial Reporting Fiscal Year (YYYY) |  |
| Number of times to close the book |  |
| Registered for Indirect Tax |  |
| VAT Taxpayer Type (China + Indirect Tax) |  |
| FX Revaluation Rate Method |  |
| Primary GAAP |  |
| Secondary GAAP 1 |  |
| Secondary GAAP 2 |  |
| Is head entity of a consolidated group |  |

## Appointments
Officers and other appointed officials for the entity.

**Add Appointment**
| Contact* | Job Title | Signing Authority* | Appointment Date | Expiration Date |
|----------|-----------|-------------------|------------------|-----------------|
|          |           |                   |                  |                 |

---

## Attributes
Custom attributes of the entity. Can be displayed on org chart if desired. Supports both number and text data points.

**Add Attribute**
| Name* | Value* |
|-------|--------|
|       |        |

---

## BEPS Pillar 2
Data points related to BEPS compliance and the KBAT application.

**GloBE Type**
Select one: Constituent Entity, Excluded Entity, Joint Venture, Joint Venture Subsidiary, Minority Owned Constituent Entity, Non Constituent Entity

**Non-Material Constituent Entity**
☐ Yes

**Investment Entity**
☐ Yes

**Stateless**
☐ Yes

**Flow-Through Entity**
☐ Yes

**Parent Entity Type**
Select one: Intermediate Parent Entity, Minority-Owned Parent Entity, Minority-Owned Subsidiary, None, Partially-owned Parent Entity, Ultimate Parent Entity

---

## Contacts
Points of contact for the entity.

**Add Contact**
| Contact (GEM)* |
|----------------|
|                |

---

## Documents
Links to key documents for the entity.

**Add Document**
| Document Name* | Document URL* | Signed Date* |
|---------------|---------------|--------------|
|               |               |              |

---

## Entity Codes
Identification numbers of the entity in other systems, such as tax filing engines and calculation engines.

**Add Entity Code**
| Name* | Value* |
|-------|--------|
|       |        |

---

## Intercompany Transactions
Loans between entities of the client. Will soon be expanded to support other types of intercompany transactions.

**Add Transactions**
| Source Entity* | Transaction Type* | Filing Period |
|---------------|------------------|---------------|
|               |                  |               |

**Transaction Amounts**
| Transaction* | Amount Type* | Value* | Currency* |
|-------------|-------------|--------|-----------|
|             |             |        |           |

**Transaction Attributes**
| Transaction* | Attribute* | Value* | Is Primary |
|-------------|-----------|--------|------------|
|             |           |        |            |

---

## Jurisdiction Classifications
More granular classifications of an entity beyond the entity type. These are specific to a jurisdiction and a classification type (legal, tax, or regulatory).

**Add Classification**
| Jurisdiction* | Jurisdiction Classification* | Entity Classification* | Entity Type* | Effective Date | Termination Date | Code | Id |
|--------------|----------------------------|----------------------|--------------|---------------|-----------------|------|-----|
|              |                            |                      |              |               |                 |      |     |

---

## Jurisdiction EINs
Tax and legal identification numbers for the entity. These are specific to a jurisdiction.

**Add EIN**
| Jurisdiction* | Jurisdiction EIN* | Tax Type |
|--------------|------------------|----------|
|              |                  |          |

---

## Jurisdiction Third Parties
Restrict entity's availability in third party document libraries.

**Add Jurisdiction Third Party**
| Jurisdiction* | Third Party Organization* |
|--------------|--------------------------|
|              |                          |

---

## Ledgers
Client ERP systems used to store the entity's data under various ledger types (GAAP, Stat, Tax).

**Add Ledger**
| Ledger Type* | Ledger* |
|-------------|---------|
|             |         |

---

## Owners
Individuals and other entities that have an ownership interest in this entity.

**Add Owner**
| Entity | Individual | Percent Owned* | Share Class | Shares Held | Entry As Shareholder Date | Is Primary Owner |
|--------|-----------|---------------|-------------|-------------|---------------------------|-----------------|
|        |           |               |             |             |                           |                 |

**Summary**
- Hidden Percentage: 0%
- Total Ownership Percentage: 0%

---

## Real Estate Ownerships
Properties owned by the entity.

**Add Real Estate**
| Name* | Jurisdiction* | Real Estate Type* | Fair Market Value* | Tax Book Value* |
|-------|--------------|------------------|-------------------|----------------|
|       |              |                  |                   |                |

---

## Source System Codes
Client ERP systems used to store the entity's data. Used to connect those ERP systems to DG's Data Ecosystem for data intake and processing.

**Add Source System Code**
| Source System* | Code* | Name | Currency* | Data Segments* | Is Primary |
|---------------|-------|------|-----------|---------------|------------|
|               |       |      |           |               |            |	
